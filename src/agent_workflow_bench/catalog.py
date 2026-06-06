from __future__ import annotations

import json
from pathlib import Path

from agent_workflow_bench.models import TaskSpec, WorkflowRole, WorkflowSpec


def load_task(path: str | Path) -> TaskSpec:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return TaskSpec(
        task_id=data["task_id"],
        title=data["title"],
        domain=data["domain"],
        objective=data["objective"],
        success_criteria=list(data.get("success_criteria", [])),
        constraints=list(data.get("constraints", [])),
        allowed_tools=list(data.get("allowed_tools", [])),
        hints=list(data.get("hints", [])),
        judge=dict(data.get("judge", {})),
    )


def load_workflow(path: str | Path) -> WorkflowSpec:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    roles = [
        WorkflowRole(
            role=item["role"],
            agent=item["agent"],
            purpose=item["purpose"],
        )
        for item in data.get("roles", [])
    ]
    return WorkflowSpec(
        workflow_id=data["workflow_id"],
        title=data["title"],
        roles=roles,
        notes=list(data.get("notes", [])),
    )
