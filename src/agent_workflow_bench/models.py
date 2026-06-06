from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class TaskSpec:
    task_id: str
    title: str
    domain: str
    objective: str
    success_criteria: list[str]
    constraints: list[str] = field(default_factory=list)
    allowed_tools: list[str] = field(default_factory=list)
    hints: list[str] = field(default_factory=list)
    judge: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WorkflowRole:
    role: str
    agent: str
    purpose: str


@dataclass(slots=True)
class WorkflowSpec:
    workflow_id: str
    title: str
    roles: list[WorkflowRole]
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class BenchmarkRun:
    run_id: str
    task: TaskSpec
    workflow: WorkflowSpec
    mode: str
    status: str
    metrics: dict[str, Any]
    artifacts: dict[str, str]
    evaluation: dict[str, Any] = field(default_factory=dict)
