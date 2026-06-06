from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from agent_workflow_bench.catalog import load_task
from agent_workflow_bench.judges import evaluate_text
from agent_workflow_bench.pipeline import build_verifier_assessment, build_verifier_report


ROOT = Path(__file__).resolve().parents[1]


def test_simulated_pipeline_generates_reviewable_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "runs"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_benchmark.py",
            "--task",
            "tasks/docs/due_diligence_summary.json",
            "--workflow",
            "workflows/planner_executor_reviewer_verifier.json",
            "--runner",
            "simulated_pipeline",
            "--out",
            str(out_dir),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    manifests = list(out_dir.glob("*.json"))
    assert len(manifests) == 1

    payload = json.loads(manifests[0].read_text(encoding="utf-8"))
    run = payload["run"]
    assert run["mode"] == "simulated-pipeline"
    assert run["status"] == "reviewed"
    assert run["metrics"]["pass_rate"] == 1.0
    assert run["metrics"]["verifier_pass"] is True
    assert run["metrics"]["evidence_coverage"] == 1.0
    assert run["metrics"]["risk_flag_count"] == 0
    assert run["metrics"]["human_takeover_recommended"] is False
    assert run["evaluation"]["review_mode"] == "simulated-reviewer-plus-rubric"
    assert run["evaluation"]["verifier"]["decision"] == "accept_with_notes"
    assert run["evaluation"]["verifier"]["evidence_coverage"] == 1.0
    assert run["evaluation"]["verifier"]["risk_flags"] == []

    artifacts = run["artifacts"]
    for key in ["planner_note", "candidate_output", "review_note", "verifier_report"]:
        path = Path(artifacts[key])
        assert path.exists(), key
        assert path.read_text(encoding="utf-8").strip(), key
    verifier_report = Path(artifacts["verifier_report"]).read_text(encoding="utf-8")
    assert "## Evidence Coverage" in verifier_report
    assert "## Risk Flags" in verifier_report
    assert "## Human Takeover Recommendation" in verifier_report


def test_verifier_recommends_human_takeover_for_coverage_gaps() -> None:
    task = load_task(ROOT / "tasks/docs/due_diligence_summary.json")
    candidate = "This is a concise summary, but it omits the required risk and evidence discussion."
    judge = evaluate_text(task, candidate)

    assessment = build_verifier_assessment(task, judge, candidate)
    report = build_verifier_report(task, judge, candidate)

    assert assessment["decision"] == "escalate_for_human_review"
    assert assessment["human_takeover_recommended"] is True
    assert "coverage_gap" in assessment["risk_flags"]
    assert "## Human Takeover Recommendation" in report
    assert "- Recommended: True" in report


def test_candidate_file_run_writes_verifier_takeover_artifact(tmp_path: Path) -> None:
    out_dir = tmp_path / "runs"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_benchmark.py",
            "--task",
            "tasks/docs/due_diligence_summary.json",
            "--workflow",
            "workflows/planner_executor_reviewer_verifier.json",
            "--candidate-file",
            "examples/due_diligence_bad_answer.txt",
            "--out",
            str(out_dir),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    manifests = list(out_dir.glob("*.json"))
    assert len(manifests) == 1

    run = json.loads(manifests[0].read_text(encoding="utf-8"))["run"]
    assert run["mode"] == "evaluated"
    assert run["metrics"]["pass_rate"] == 0.0
    assert run["metrics"]["human_takeover_recommended"] is True
    assert run["metrics"]["risk_flag_count"] >= 1
    assert run["evaluation"]["verifier"]["decision"] == "escalate_for_human_review"
    assert "coverage_gap" in run["evaluation"]["verifier"]["risk_flags"]

    verifier_report = Path(run["artifacts"]["verifier_report"])
    assert verifier_report.exists()
    verifier_text = verifier_report.read_text(encoding="utf-8")
    assert "Decision: escalate_for_human_review" in verifier_text
    assert "coverage_gap" in verifier_text
