from __future__ import annotations

import json
from pathlib import Path

from agent_workflow_bench.reporting import build_summary, render_markdown_report


def write_manifest(path: Path, run_id: str, workflow_id: str, pass_rate: float | None, failure_types: list[str]) -> None:
    payload = {
        "generated_at": "2026-06-06T00:00:00+00:00",
        "run": {
            "run_id": run_id,
            "task": {"task_id": "task-1", "title": "Task One", "domain": "docs"},
            "workflow": {"workflow_id": workflow_id, "title": "Workflow", "roles": []},
            "mode": "simulated-pipeline",
            "status": "reviewed" if pass_rate == 1.0 else "scored",
            "metrics": {
                "pass_rate": pass_rate,
                "latency_seconds": 2.5,
                "human_takeovers": 0,
                "verifier_pass": pass_rate == 1.0 if pass_rate is not None else None,
            },
            "artifacts": {"candidate_output": "candidate.md"},
            "evaluation": {
                "score": pass_rate,
                "failure_types": failure_types,
            },
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_build_summary_groups_workflows_and_failure_types(tmp_path: Path) -> None:
    write_manifest(tmp_path / "run-1.json", "run-1", "workflow-a", 1.0, [])
    write_manifest(tmp_path / "run-2.json", "run-2", "workflow-a", 0.0, ["coverage_gap"])
    write_manifest(tmp_path / "run-3.json", "run-3", "workflow-b", None, ["timeout"])

    summary = build_summary(tmp_path)

    assert summary["run_count"] == 3
    assert summary["evaluated_run_count"] == 2
    assert summary["overall"]["avg_pass_rate"] == 0.5
    assert summary["overall"]["failure_type_counts"] == {"coverage_gap": 1, "timeout": 1}
    workflow_a = next(item for item in summary["workflow_summary"] if item["workflow_id"] == "workflow-a")
    assert workflow_a["runs"] == 2
    assert workflow_a["evaluated_runs"] == 2
    assert workflow_a["avg_pass_rate"] == 0.5


def test_build_summary_ignores_summary_json_artifacts(tmp_path: Path) -> None:
    write_manifest(tmp_path / "run-1.json", "run-1", "workflow-a", 1.0, [])
    (tmp_path / "summary.json").write_text(
        json.dumps({"run_count": 1, "workflow_summary": []}),
        encoding="utf-8",
    )

    summary = build_summary(tmp_path)

    assert summary["run_count"] == 1
    assert summary["runs"][0]["run_id"] == "run-1"


def test_render_markdown_report_contains_recruiter_readable_sections(tmp_path: Path) -> None:
    write_manifest(tmp_path / "run-1.json", "run-1", "workflow-a", 1.0, [])
    write_manifest(tmp_path / "run-2.json", "run-2", "workflow-a", 0.0, ["coverage_gap"])

    markdown = render_markdown_report(build_summary(tmp_path), title="Agent Workflow Report")

    assert "# Agent Workflow Report" in markdown
    assert "## Overall Metrics" in markdown
    assert "workflow-a" in markdown
    assert "coverage_gap" in markdown
    assert "avg pass rate" in markdown.lower()
