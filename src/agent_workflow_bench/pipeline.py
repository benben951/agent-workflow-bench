from __future__ import annotations

from pathlib import Path

from agent_workflow_bench.judges import JudgeResult
from agent_workflow_bench.models import TaskSpec, WorkflowSpec


RISK_TERMS = {
    "fabricated_citation": ["fabricated citation", "fake citation", "made-up citation"],
    "missing_evidence": ["missing evidence", "insufficient evidence", "not enough evidence"],
    "unsafe_certainty": ["definitely", "guaranteed", "no risk", "approved"],
}


def build_planner_prompt(task: TaskSpec, workflow: WorkflowSpec) -> str:
    role_names = " -> ".join(role.role for role in workflow.roles)
    lines = [
        f"Task: {task.title}",
        "",
        f"Objective: {task.objective}",
        "",
        f"Workflow roles: {role_names}",
        "",
        "Write a concise markdown execution plan.",
        "Include:",
        "- what files, symbols, or evidence should be inspected first",
        "- what the executor should produce",
        "- how the reviewer should judge success",
    ]
    if task.success_criteria:
        lines.extend(["", "Success criteria:"])
        lines.extend([f"- {item}" for item in task.success_criteria])
    if task.constraints:
        lines.extend(["", "Constraints:"])
        lines.extend([f"- {item}" for item in task.constraints])
    return "\n".join(lines)


def build_plan_text(task: TaskSpec, workflow: WorkflowSpec) -> str:
    role_names = " -> ".join(role.role for role in workflow.roles)
    lines = [
        f"# Plan for {task.task_id}",
        "",
        f"Workflow: {workflow.workflow_id}",
        f"Roles: {role_names}",
        "",
        "## Objective",
        task.objective,
        "",
        "## Planned Steps",
        "1. Find the most relevant files, symbols, or evidence for the task.",
        "2. Produce a concise answer that directly targets the success criteria.",
        "3. Run a reviewer or verifier pass before finalizing the answer.",
    ]
    if task.constraints:
        lines.extend(["", "## Constraints"])
        lines.extend([f"- {item}" for item in task.constraints])
    if task.success_criteria:
        lines.extend(["", "## Success Criteria"])
        lines.extend([f"- {item}" for item in task.success_criteria])
    return "\n".join(lines)


def build_review_prompt(task: TaskSpec, candidate_text: str, plan_text: str | None = None) -> str:
    lines = [
        f"Task: {task.title}",
        "",
        f"Objective: {task.objective}",
    ]
    if task.success_criteria:
        lines.extend(["", "Success criteria:"])
        lines.extend([f"- {item}" for item in task.success_criteria])
    if task.constraints:
        lines.extend(["", "Constraints:"])
        lines.extend([f"- {item}" for item in task.constraints])
    if plan_text:
        lines.extend(["", "Planner note:", plan_text[:2000]])
    lines.extend(
        [
            "",
            "Candidate output:",
            candidate_text[:4000],
            "",
            "Review this output and return concise markdown with these sections:",
            "- Verdict: PASS or FAIL",
            "- Missing criteria",
            "- Risks or ambiguity",
            "- Suggested revision",
        ]
    )
    return "\n".join(lines)


def build_review_text(task: TaskSpec, judge: JudgeResult, candidate_text: str) -> str:
    lines = [
        f"# Review for {task.task_id}",
        "",
        f"Pass: {judge.passed}",
        f"Score: {judge.score}",
        "",
        "## Notes",
    ]
    lines.extend([f"- {item}" for item in judge.notes] or ["- No review notes."])
    lines.extend(["", "## Missing Keywords"])
    lines.extend([f"- {item}" for item in judge.missing_keywords] or ["- None"])
    lines.extend(["", "## Matched Keywords"])
    lines.extend([f"- {item}" for item in judge.matched_keywords] or ["- None"])
    lines.extend(
        [
            "",
            "## Reviewer Suggestion",
            "Keep the final answer short, structural, and explicitly tied to the task success criteria.",
            "",
            "## Candidate Preview",
            candidate_text[:1500],
        ]
    )
    return "\n".join(lines)


def build_simulated_candidate_text(task: TaskSpec, plan_text: str) -> str:
    lines = [
        f"# Candidate Output for {task.task_id}",
        "",
        "## Concise Summary",
        f"This simulated executor output addresses the objective: {task.objective}",
        "",
        "## Evidence-backed Risk Points",
    ]
    criteria = task.success_criteria or ["Provide a direct answer tied to the task objective."]
    for index, item in enumerate(criteria, start=1):
        lines.append(f"{index}. Risk and evidence note: {item}")
    lines.extend(
        [
            "",
            "## Uncertainty and Missing Information",
            "Uncertainty remains where source evidence is incomplete. Missing information should be flagged for analyst review instead of guessed.",
            "",
            "## Analyst-Readable Next Step",
            "Use this output as a reviewable draft, then apply the verifier rubric before relying on it.",
            "",
            "## Planner Trace",
            plan_text[:1000],
        ]
    )
    return "\n".join(lines)


def build_verifier_assessment(task: TaskSpec, judge: JudgeResult, candidate_text: str) -> dict:
    lower = candidate_text.lower()
    total_keywords = len(judge.matched_keywords) + len(judge.missing_keywords)
    evidence_coverage = 1.0 if total_keywords == 0 else round(len(judge.matched_keywords) / total_keywords, 3)

    risk_flags: list[str] = []
    if judge.missing_keywords:
        risk_flags.append("coverage_gap")
    for flag, terms in RISK_TERMS.items():
        if any(term in lower for term in terms):
            risk_flags.append(flag)

    # "Flag missing evidence" is a safe caveat, not a risk by itself.
    if "missing_evidence" in risk_flags and "flag missing evidence" in lower:
        risk_flags.remove("missing_evidence")

    human_takeover = (not judge.passed) or any(flag in risk_flags for flag in {"fabricated_citation", "unsafe_certainty"})
    decision = "escalate_for_human_review" if human_takeover else "accept_with_notes"

    return {
        "decision": decision,
        "evidence_coverage": evidence_coverage,
        "risk_flags": risk_flags,
        "human_takeover_recommended": human_takeover,
    }


def build_verifier_report(task: TaskSpec, judge: JudgeResult, candidate_text: str = "") -> str:
    assessment = build_verifier_assessment(task, judge, candidate_text)
    verdict = "PASS" if judge.passed else "FAIL"
    lines = [
        f"# Verifier Report for {task.task_id}",
        "",
        f"Verdict: {verdict}",
        f"Score: {judge.score}",
        f"Decision: {assessment['decision']}",
        "",
        "## Evidence Coverage",
        f"- Coverage: {assessment['evidence_coverage']}",
        f"- Matched signals: {len(judge.matched_keywords)}",
        f"- Missing signals: {len(judge.missing_keywords)}",
        "",
        "## Risk Flags",
    ]
    lines.extend([f"- {item}" for item in assessment["risk_flags"]] or ["- None"])
    lines.extend(
        [
            "",
            "## Human Takeover Recommendation",
            f"- Recommended: {assessment['human_takeover_recommended']}",
            "",
            "## Matched Keywords",
        ]
    )
    lines.extend([f"- {item}" for item in judge.matched_keywords] or ["- None"])
    lines.extend(["", "## Missing Keywords"])
    lines.extend([f"- {item}" for item in judge.missing_keywords] or ["- None"])
    lines.extend(["", "## Failure Types"])
    lines.extend([f"- {item}" for item in judge.failure_types] or ["- None"])
    lines.extend(["", "## Notes"])
    lines.extend([f"- {item}" for item in judge.notes] or ["- No verifier notes."])
    return "\n".join(lines)


def write_text_artifact(path: str | Path, content: str) -> str:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    return str(out.resolve())
