from __future__ import annotations

from pathlib import Path

from agent_workflow_bench.judges import JudgeResult
from agent_workflow_bench.models import TaskSpec, WorkflowSpec


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


def write_text_artifact(path: str | Path, content: str) -> str:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    return str(out.resolve())
