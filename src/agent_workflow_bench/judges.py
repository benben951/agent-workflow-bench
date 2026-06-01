from __future__ import annotations

from dataclasses import dataclass

from agent_workflow_bench.models import TaskSpec


@dataclass(slots=True)
class JudgeResult:
    passed: bool
    score: float
    matched_keywords: list[str]
    missing_keywords: list[str]
    notes: list[str]
    failure_types: list[str]


def evaluate_text(task: TaskSpec, candidate_text: str) -> JudgeResult:
    judge_cfg = task.judge or {}
    required_keywords = [str(item).strip() for item in judge_cfg.get("required_keywords", []) if str(item).strip()]
    optional_keywords = [str(item).strip() for item in judge_cfg.get("optional_keywords", []) if str(item).strip()]

    lower = candidate_text.lower()
    matched_required = [kw for kw in required_keywords if kw.lower() in lower]
    missing_required = [kw for kw in required_keywords if kw.lower() not in lower]
    matched_optional = [kw for kw in optional_keywords if kw.lower() in lower]

    total_slots = len(required_keywords) + len(optional_keywords)
    raw_hits = len(matched_required) + len(matched_optional)
    score = 1.0 if total_slots == 0 else round(raw_hits / total_slots, 3)
    passed = not missing_required

    notes: list[str] = []
    failure_types: list[str] = []
    if missing_required:
        notes.append("Missing one or more required concepts.")
        failure_types.append("coverage_gap")
    if passed:
        notes.append("All required concepts are present.")
    if "missing" in lower and "evidence" in lower:
        notes.append("Candidate explicitly acknowledged missing evidence.")
    if "do not modify files" in lower:
        notes.append("Candidate appears to echo task constraints.")

    return JudgeResult(
        passed=passed,
        score=score,
        matched_keywords=matched_required + matched_optional,
        missing_keywords=missing_required,
        notes=notes,
        failure_types=failure_types,
    )
