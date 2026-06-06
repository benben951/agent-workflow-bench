from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any


def load_run_manifest(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    return payload["run"]


def iter_run_manifests(run_dir: str | Path) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    for path in sorted(Path(run_dir).glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        run = payload.get("run")
        if isinstance(run, dict):
            runs.append(run)
    return runs


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _avg(values: list[float]) -> float | None:
    if not values:
        return None
    return round(mean(values), 3)


def build_summary(run_dir: str | Path) -> dict[str, Any]:
    runs: list[dict[str, Any]] = []
    workflow_buckets: dict[str, list[dict[str, Any]]] = {}
    failure_counts: Counter[str] = Counter()
    pass_rates: list[float] = []
    latencies: list[float] = []

    for run in iter_run_manifests(run_dir):
        workflow_id = run["workflow"]["workflow_id"]
        metrics = run.get("metrics", {})
        evaluation = run.get("evaluation", {})
        pass_rate = _safe_float(metrics.get("pass_rate"))
        latency = _safe_float(metrics.get("latency_seconds"))
        failure_types = list(evaluation.get("failure_types", []) or [])

        if pass_rate is not None:
            pass_rates.append(pass_rate)
        if latency is not None:
            latencies.append(latency)
        failure_counts.update(failure_types)

        row = {
            "run_id": run["run_id"],
            "task_id": run["task"]["task_id"],
            "workflow_id": workflow_id,
            "mode": run["mode"],
            "status": run["status"],
            "pass_rate": pass_rate,
            "latency_seconds": latency,
            "score": evaluation.get("score") if evaluation else None,
            "failure_types": failure_types,
            "artifact_count": len(run.get("artifacts", {})),
        }
        runs.append(row)
        workflow_buckets.setdefault(workflow_id, []).append(row)

    workflow_summary = []
    for workflow_id, rows in sorted(workflow_buckets.items()):
        workflow_pass_rates = [row["pass_rate"] for row in rows if row["pass_rate"] is not None]
        workflow_latencies = [row["latency_seconds"] for row in rows if row["latency_seconds"] is not None]
        workflow_failures: Counter[str] = Counter()
        for row in rows:
            workflow_failures.update(row["failure_types"])
        workflow_summary.append(
            {
                "workflow_id": workflow_id,
                "runs": len(rows),
                "evaluated_runs": len(workflow_pass_rates),
                "avg_pass_rate": _avg(workflow_pass_rates),
                "avg_latency_seconds": _avg(workflow_latencies),
                "failure_type_counts": dict(sorted(workflow_failures.items())),
            }
        )

    return {
        "run_count": len(runs),
        "evaluated_run_count": len(pass_rates),
        "overall": {
            "avg_pass_rate": _avg(pass_rates),
            "avg_latency_seconds": _avg(latencies),
            "failure_type_counts": dict(sorted(failure_counts.items())),
        },
        "workflow_summary": workflow_summary,
        "runs": runs,
    }


def _fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    return str(value)


def render_markdown_report(summary: dict[str, Any], title: str = "Agent Workflow Benchmark Report") -> str:
    lines = [
        f"# {title}",
        "",
        "## Overall Metrics",
        "",
        f"- Run count: {summary['run_count']}",
        f"- Evaluated run count: {summary['evaluated_run_count']}",
        f"- Avg pass rate: {_fmt(summary['overall']['avg_pass_rate'])}",
        f"- Avg latency seconds: {_fmt(summary['overall']['avg_latency_seconds'])}",
        "",
        "## Failure Types",
        "",
    ]
    failure_counts = summary["overall"]["failure_type_counts"]
    if failure_counts:
        lines.extend(f"- {name}: {count}" for name, count in failure_counts.items())
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Workflow Summary",
            "",
            "| Workflow | Runs | Evaluated | Avg pass rate | Avg latency seconds | Failure types |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for item in summary["workflow_summary"]:
        failures = ", ".join(f"{name}:{count}" for name, count in item["failure_type_counts"].items()) or "None"
        lines.append(
            "| {workflow_id} | {runs} | {evaluated_runs} | {avg_pass_rate} | {avg_latency_seconds} | {failures} |".format(
                workflow_id=item["workflow_id"],
                runs=item["runs"],
                evaluated_runs=item["evaluated_runs"],
                avg_pass_rate=_fmt(item["avg_pass_rate"]),
                avg_latency_seconds=_fmt(item["avg_latency_seconds"]),
                failures=failures,
            )
        )

    lines.extend(
        [
            "",
            "## Run Details",
            "",
            "| Run | Task | Workflow | Mode | Status | Pass rate | Score | Failure types | Artifacts |",
            "|---|---|---|---|---|---:|---:|---|---:|",
        ]
    )
    for run in summary["runs"]:
        failures = ", ".join(run["failure_types"]) or "None"
        lines.append(
            "| {run_id} | {task_id} | {workflow_id} | {mode} | {status} | {pass_rate} | {score} | {failures} | {artifact_count} |".format(
                run_id=run["run_id"],
                task_id=run["task_id"],
                workflow_id=run["workflow_id"],
                mode=run["mode"],
                status=run["status"],
                pass_rate=_fmt(run["pass_rate"]),
                score=_fmt(run["score"]),
                failures=failures,
                artifact_count=run["artifact_count"],
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This report is intended for workflow comparison, not model leaderboard claims. A strong workflow should improve pass rate, reduce recurring failure types, preserve verifier artifacts, and keep human takeover paths visible.",
        ]
    )
    return "\n".join(lines) + "\n"
