from __future__ import annotations

import json
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from agent_workflow_bench.catalog import load_task, load_workflow
from agent_workflow_bench.judges import evaluate_text
from agent_workflow_bench.models import BenchmarkRun


def build_run_manifest(
    task_path: str | Path,
    workflow_path: str | Path,
    out_dir: str | Path,
    candidate_text: str | None = None,
    candidate_path: str | Path | None = None,
    mode: str | None = None,
    status: str | None = None,
    extra_metrics: dict | None = None,
    extra_artifacts: dict | None = None,
    extra_evaluation: dict | None = None,
) -> Path:
    task = load_task(task_path)
    workflow = load_workflow(workflow_path)
    run_id = f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"

    out_root = Path(out_dir)
    out_root.mkdir(parents=True, exist_ok=True)
    run_path = out_root / f"{run_id}.json"

    run = BenchmarkRun(
        run_id=run_id,
        task=task,
        workflow=workflow,
        mode=mode or ("evaluated" if candidate_text else "dry-run"),
        status=status or ("scored" if candidate_text else "planned"),
        metrics={
            "pass_rate": None,
            "first_pass_success": None,
            "latency_seconds": None,
            "cost_usd": None,
            "human_takeovers": 0,
        },
        artifacts={
            "task_spec": str(Path(task_path).resolve()),
            "workflow_spec": str(Path(workflow_path).resolve()),
        },
    )

    if candidate_path is not None:
        run.artifacts["candidate_output"] = str(Path(candidate_path).resolve())
    if extra_artifacts:
        run.artifacts.update(extra_artifacts)

    if candidate_text:
        judged = evaluate_text(task, candidate_text)
        run.metrics["pass_rate"] = 1.0 if judged.passed else 0.0
        run.metrics["first_pass_success"] = 1.0 if judged.passed else 0.0
        run.evaluation = {
            "passed": judged.passed,
            "score": judged.score,
            "matched_keywords": judged.matched_keywords,
            "missing_keywords": judged.missing_keywords,
            "notes": judged.notes,
            "failure_types": judged.failure_types,
        }
    if extra_metrics:
        run.metrics.update(extra_metrics)
    if extra_evaluation:
        run.evaluation.update(extra_evaluation)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run": asdict(run),
    }
    run_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return run_path
