"""Simple dialog orchestrator for CLI demo with early termination and audit."""
from __future__ import annotations

import uuid
from collections import Counter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import models
from .rules_repo import RulesRepo
from .question_builder import needed_feature_keys, build_questions
from .evaluators.jsonlogic_eval import evaluate_rule
from .classifiers.aggregator import classify
from .partial_eval import eval3, collect_vars, TRUE
from sqlalchemy import text as sql_text

PRIORITY = ["prohibited", "high_risk", "limited_risk", "minimal_risk"]


class DialogOrchestrator:
    def __init__(self, db_url: str):
        if db_url.startswith("sqlite"):
            self.engine = create_engine(db_url, connect_args={"check_same_thread": False})
        else:
            self.engine = create_engine(db_url, pool_recycle=3600, pool_size=5)
        self.Session = sessionmaker(bind=self.engine)

    def start_session(self, customer_id: str = None) -> str:
        with self.Session() as db:
            repo = RulesRepo(db)
            _, _, _, version = repo.load()
            session_id = str(uuid.uuid4())
            chat = models.ChatSession(
                id=session_id, customer_id=customer_id, rule_snapshot_version=version
            )
            db.add(chat)
            db.commit()
            return session_id

    def _triage_state(self, rules, answers):
        state = {cat: {"any_true": False, "any_unknown": False, "unknown_rules": []} for cat in PRIORITY}
        for r in rules:
            s = eval3(r.condition, answers)
            if s == TRUE:
                state[r.category]["any_true"] = True
            elif s == "UNKNOWN":
                state[r.category]["any_unknown"] = True
                state[r.category]["unknown_rules"].append(r)
        return state

    def _pick_next_feature_for_top_unknown(self, top_unknown_rules, answers, questions_db, feats):
        counter = Counter()
        for r in top_unknown_rules:
            for k in collect_vars(r.condition):
                if k not in answers:
                    counter[k] += 1
        if not counter:
            return None
        best_key, _ = counter.most_common(1)[0]
        for q in sorted(questions_db, key=lambda q: getattr(q, "priority", 0)):
            if q.feature_key == best_key:
                if not q.gating or evaluate_rule(q.gating, answers):
                    f = feats[best_key]
                    return {
                        "feature_key": best_key,
                        "prompt": q.prompt_en or f.prompt_en,
                        "type": f.type,
                        "options": f.options,
                    }
        if best_key in feats:
            f = feats[best_key]
            return {
                "feature_key": best_key,
                "prompt": f.prompt_en,
                "type": f.type,
                "options": f.options,
            }
        return None

    def next_question(self, session_id: str):
        with self.Session() as db:
            chat = db.get(models.ChatSession, session_id)
            if not chat:
                raise RuntimeError(f"Chat session not found: {session_id}")
            repo = RulesRepo(db)
            rules, feats, qs, version = repo.load()
            answers = {a.feature_key: a.value for a in chat.answers}

            def finalize():
                rule_evals = []
                evaluated = []
                for r in rules:
                    state = eval3(r.condition, answers)
                    rule_evals.append({"id": r.id, "category": r.category, "state": state})
                    evaluated.append({
                        "id": r.id,
                        "category": r.category,
                        "weight": r.weight,
                        "legal_refs": r.legal_refs,
                        "matched": state == TRUE,
                    })
                outcome = classify(evaluated, answers)
                reasoning = {"outcome": outcome, "rule_evaluations": rule_evals}
                res = models.RiskOutcome(
                    id=str(uuid.uuid4()),
                    session_id=session_id,
                    rule_snapshot_version=version,
                    category=outcome["category"],
                    score=outcome["score"],
                    reasoning=reasoning,
                    legal_refs=outcome["legal_refs"],
                    exception_applied=outcome["exception_applied"],
                )
                db.add(res)
                db.commit()
                return {"outcome": outcome, "rule_evaluations": rule_evals}

            triage = self._triage_state(rules, answers)
            if triage["prohibited"]["any_true"]:
                return finalize()

            def category_decidable(cat: str) -> bool:
                idx = PRIORITY.index(cat)
                higher = PRIORITY[:idx]
                return all(not (triage[h]["any_unknown"] or triage[h]["any_true"]) for h in higher)

            for cat in ["high_risk", "limited_risk"]:
                if category_decidable(cat) and triage[cat]["any_true"]:
                    return finalize()

            for cat in ["prohibited", "high_risk", "limited_risk"]:
                if triage[cat]["any_unknown"]:
                    nxt = self._pick_next_feature_for_top_unknown(
                        triage[cat]["unknown_rules"], answers, qs, feats
                    )
                    if nxt:
                        # динамически сузим опции для annex3_item по выбранной области
                        if nxt["feature_key"] == "annex3_item":
                            area = answers.get("annex3_area")
                            if area:
                                rows = db.execute(sql_text("""
                                    SELECT section_code, COALESCE(title,'') AS title, COALESCE(content,'') AS content
                                    FROM rules
                                    WHERE section_code LIKE 'AnnexIII.%'
                                    ORDER BY section_code
                                """)).fetchall()
                                # соберём подчинённые пункты выбранной области
                                opts = []
                                prefix = area + "."
                                for sc, _, _ in rows:
                                    if sc.startswith(prefix) and sc.count('.') == 2:
                                        opts.append(sc)
                                # если у области нет подпунктов — оставим саму область
                                if not opts:
                                    opts = [area]
                                nxt["options"] = opts
                        return nxt
                    break

            needed = needed_feature_keys(rules)
            needed |= {k for k, f in feats.items() if getattr(f, "required", False)}
            missing = [k for k in needed if k not in answers]
            if missing:
                missing_set = set(missing)
                candidates = [
                    q
                    for q in qs
                    if q.feature_key in missing_set
                    and (not q.gating or evaluate_rule(q.gating, answers))
                ]
                candidates.sort(key=lambda q: getattr(q, "priority", 0))
                if candidates:
                    q = candidates[0]
                    f = feats[q.feature_key]
                    res = {
                        "feature_key": q.feature_key,
                        "prompt": q.prompt_en or f.prompt_en,
                        "type": f.type,
                        "options": f.options,
                    }
                    if q.feature_key == "annex3_item":
                        area = answers.get("annex3_area")
                        if area:
                            rows = db.execute(sql_text("""
                                SELECT section_code FROM rules
                                WHERE section_code LIKE 'AnnexIII.%'
                                ORDER BY section_code
                            """)).fetchall()
                            prefix = area + "."
                            opts = [r[0] for r in rows if r[0].startswith(prefix) and r[0].count(".")==2] or [area]
                            res["options"] = opts
                    return res
                raise RuntimeError(f"Missing answers for: {', '.join(missing)}")

            questions = []
            for q in qs:
                if q.feature_key in answers:
                    continue
                if q.gating and not evaluate_rule(q.gating, answers):
                    continue
                questions.append(q)
            if questions:
                q = sorted(questions, key=lambda q: getattr(q, "priority", 0))[0]
                f = feats[q.feature_key]
                res = {
                    "feature_key": q.feature_key,
                    "prompt": q.prompt_en or f.prompt_en,
                    "type": f.type,
                    "options": f.options,
                }
                if q.feature_key == "annex3_item":
                    area = answers.get("annex3_area")
                    if area:
                        rows = db.execute(sql_text("""
                            SELECT section_code FROM rules
                            WHERE section_code LIKE 'AnnexIII.%'
                            ORDER BY section_code
                        """)).fetchall()
                        prefix = area + "."
                        opts = [r[0] for r in rows if r[0].startswith(prefix) and r[0].count(".")==2] or [area]
                        res["options"] = opts
                return res

            return finalize()

    def submit_answer(self, session_id: str, feature_key: str, value):
        with self.Session() as db:
            if not db.get(models.ChatSession, session_id):
                raise RuntimeError(f"Chat session not found: {session_id}")
            ans = models.ChatAnswer(
                id=str(uuid.uuid4()),
                session_id=session_id,
                feature_key=feature_key,
                value=value,
            )
            db.add(ans)
            db.commit()
