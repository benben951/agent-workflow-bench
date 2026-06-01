from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize benchmark run manifests.")
    parser.add_argument("--runs", default="outputs/runs", help="Directory containing JSON run manifests")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = Path(args.runs)
    files = sorted(run_dir.glob("*.json"))
    summary = []
    workflow_stats: dict[str, dict[str, float]] = {}
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        run = payload["run"]
        workflow_id = run["workflow"]["workflow_id"]
        pass_rate = run["metrics"].get("pass_rate")
        workflow_bucket = workflow_stats.setdefault(
            workflow_id,
            {"runs": 0, "evaluated_runs": 0, "pass_sum": 0.0},
        )
        workflow_bucket["runs"] += 1
        if pass_rate is not None:
            workflow_bucket["evaluated_runs"] += 1
            workflow_bucket["pass_sum"] += float(pass_rate)
        summary.append(
            {
                "run_id": run["run_id"],
                "task_id": run["task"]["task_id"],
                "workflow_id": run["workflow"]["workflow_id"],
                "mode": run["mode"],
                "status": run["status"],
                "pass_rate": run["metrics"].get("pass_rate"),
                "latency_seconds": run["metrics"].get("latency_seconds"),
                "score": run["evaluation"].get("score") if run.get("evaluation") else None,
                "failure_types": run["evaluation"].get("failure_types", []) if run.get("evaluation") else [],
            }
        )
    workflow_summary = []
    for workflow_id, stats in workflow_stats.items():
        evaluated_runs = int(stats["evaluated_runs"])
        avg_pass_rate = None if evaluated_runs == 0 else round(stats["pass_sum"] / evaluated_runs, 3)
        workflow_summary.append(
            {
                "workflow_id": workflow_id,
                "runs": int(stats["runs"]),
                "evaluated_runs": evaluated_runs,
                "avg_pass_rate": avg_pass_rate,
            }
        )
    print(
        json.dumps(
            {
                "run_count": len(summary),
                "workflow_summary": workflow_summary,
                "runs": summary,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
