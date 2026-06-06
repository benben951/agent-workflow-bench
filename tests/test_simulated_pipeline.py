from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


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
    assert run["evaluation"]["review_mode"] == "simulated-reviewer-plus-rubric"

    artifacts = run["artifacts"]
    for key in ["planner_note", "candidate_output", "review_note", "verifier_report"]:
        path = Path(artifacts[key])
        assert path.exists(), key
        assert path.read_text(encoding="utf-8").strip(), key
