from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from agent_workflow_bench.benchmark import build_run_manifest
from agent_workflow_bench.catalog import load_task, load_workflow
from agent_workflow_bench.judges import evaluate_text
from agent_workflow_bench.pipeline import (
    build_plan_text,
    build_planner_prompt,
    build_review_prompt,
    build_review_text,
    build_simulated_candidate_text,
    build_verifier_assessment,
    build_verifier_report,
    write_text_artifact,
)
from agent_workflow_bench.runners import run_codex_executor, run_codex_prompt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a dry-run benchmark manifest for an agent workflow task.")
    parser.add_argument("--task", required=True, help="Path to a task JSON file")
    parser.add_argument("--workflow", required=True, help="Path to a workflow JSON file")
    parser.add_argument("--out", default="outputs/runs", help="Directory for generated run manifests")
    parser.add_argument("--candidate-file", help="Optional path to a candidate output text file for rubric scoring")
    parser.add_argument(
        "--runner",
        choices=["manifest", "simulated_pipeline", "codex", "codex_pipeline"],
        default="manifest",
        help="How to produce the candidate output",
    )
    parser.add_argument("--cwd", help="Workspace directory for agent execution")
    parser.add_argument("--runner-timeout", type=int, default=120, help="Timeout in seconds for live runner execution")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    task = load_task(args.task)
    workflow = load_workflow(args.workflow)
    candidate_text = None
    candidate_path = args.candidate_file
    extra_artifacts: dict[str, str] = {}
    extra_metrics: dict[str, object] = {}
    extra_evaluation: dict[str, object] = {}
    log_root = ROOT / "outputs" / "logs"

    if args.runner == "simulated_pipeline":
        artifact_root = ROOT / "outputs" / "simulated" / task.task_id
        plan_path = artifact_root / "planner_note.md"
        candidate_path = str((artifact_root / "candidate_output.md").resolve())
        review_path = artifact_root / "review_note.md"
        verifier_path = artifact_root / "verifier_report.md"

        plan_text = build_plan_text(task, workflow)
        candidate_text = build_simulated_candidate_text(task, plan_text)
        judged = evaluate_text(task, candidate_text)
        verifier = build_verifier_assessment(task, judged, candidate_text)
        review_text = build_review_text(task, judged, candidate_text)
        verifier_text = build_verifier_report(task, judged, candidate_text)

        extra_artifacts["planner_note"] = write_text_artifact(plan_path, plan_text)
        extra_artifacts["candidate_output"] = write_text_artifact(candidate_path, candidate_text)
        extra_artifacts["review_note"] = write_text_artifact(review_path, review_text)
        extra_artifacts["verifier_report"] = write_text_artifact(verifier_path, verifier_text)
        extra_metrics["latency_seconds"] = 0.0
        extra_metrics["review_findings_count"] = len(judged.missing_keywords)
        extra_metrics["verifier_pass"] = judged.passed
        extra_metrics["evidence_coverage"] = verifier["evidence_coverage"]
        extra_metrics["risk_flag_count"] = len(verifier["risk_flags"])
        extra_metrics["human_takeover_recommended"] = verifier["human_takeover_recommended"]
        extra_evaluation["review_status"] = "simulated-reviewer"
        extra_evaluation["review_mode"] = "simulated-reviewer-plus-rubric"
        extra_evaluation["failure_types"] = judged.failure_types
        extra_evaluation["verifier"] = verifier

    if args.runner in {"codex", "codex_pipeline"}:
        if not args.cwd:
            raise SystemExit("--cwd is required when --runner codex is used")
        if not candidate_path:
            task_name = Path(args.task).stem
            candidate_path = str((ROOT / "outputs" / "candidates" / f"{task_name}.txt").resolve())
        planner_note_text = None
        if args.runner == "codex_pipeline":
            plan_path = ROOT / "outputs" / "plans" / f"{Path(args.task).stem}.md"
            planner_stdout_path = log_root / f"{Path(args.task).stem}.planner.stdout.log"
            planner_stderr_path = log_root / f"{Path(args.task).stem}.planner.stderr.log"
            planner_result = run_codex_prompt(
                build_planner_prompt(task, workflow),
                args.cwd,
                plan_path,
                timeout_seconds=max(20, min(args.runner_timeout, 45)),
            )
            extra_artifacts["planner_stdout"] = write_text_artifact(planner_stdout_path, planner_result.stdout)
            extra_artifacts["planner_stderr"] = write_text_artifact(planner_stderr_path, planner_result.stderr)
            if planner_result.ok and Path(planner_result.candidate_path).exists():
                planner_note_text = Path(planner_result.candidate_path).read_text(encoding="utf-8")
                extra_artifacts["planner_note"] = str(Path(planner_result.candidate_path).resolve())
            else:
                planner_note_text = build_plan_text(task, workflow)
                extra_artifacts["planner_note"] = write_text_artifact(plan_path, planner_note_text)
                extra_evaluation["planner_status"] = planner_result.status
        result = run_codex_executor(
            args.task,
            args.cwd,
            candidate_path,
            timeout_seconds=args.runner_timeout,
            extra_instructions=planner_note_text,
        )
        stdout_path = log_root / f"{Path(args.task).stem}.stdout.log"
        stderr_path = log_root / f"{Path(args.task).stem}.stderr.log"
        extra_artifacts["runner_stdout"] = write_text_artifact(stdout_path, result.stdout)
        extra_artifacts["runner_stderr"] = write_text_artifact(stderr_path, result.stderr)
        extra_metrics["latency_seconds"] = result.duration_seconds
        extra_evaluation["runner_status"] = result.status
        extra_evaluation["runner_command"] = result.command
        if not result.ok:
            run_path = build_run_manifest(
                args.task,
                args.workflow,
                args.out,
                candidate_text=None,
                candidate_path=None,
                mode="codex-run-attempt",
                status=result.status,
                extra_metrics=extra_metrics,
                extra_artifacts=extra_artifacts,
                extra_evaluation=extra_evaluation,
            )
            print(f"Wrote benchmark manifest: {Path(run_path).resolve()}")
            raise SystemExit(
                f"Codex execution {result.status}.\n"
                f"stdout:\n{result.stdout}\n\n"
                f"stderr:\n{result.stderr}"
            )

    if candidate_path:
        candidate_text = Path(candidate_path).read_text(encoding="utf-8")
        if args.runner == "manifest":
            judged = evaluate_text(task, candidate_text)
            verifier = build_verifier_assessment(task, judged, candidate_text)
            verifier_path = ROOT / "outputs" / "verifiers" / f"{Path(args.task).stem}.md"
            extra_artifacts["verifier_report"] = write_text_artifact(
                verifier_path,
                build_verifier_report(task, judged, candidate_text),
            )
            extra_metrics["verifier_pass"] = judged.passed
            extra_metrics["evidence_coverage"] = verifier["evidence_coverage"]
            extra_metrics["risk_flag_count"] = len(verifier["risk_flags"])
            extra_metrics["human_takeover_recommended"] = verifier["human_takeover_recommended"]
            extra_evaluation["review_mode"] = "candidate-file-plus-rubric"
            extra_evaluation["failure_types"] = judged.failure_types
            extra_evaluation["verifier"] = verifier
        if args.runner == "codex_pipeline":
            judged = evaluate_text(task, candidate_text)
            review_path = ROOT / "outputs" / "reviews" / f"{Path(args.task).stem}.md"
            review_stdout_path = log_root / f"{Path(args.task).stem}.review.stdout.log"
            review_stderr_path = log_root / f"{Path(args.task).stem}.review.stderr.log"
            plan_text = None
            if "planner_note" in extra_artifacts and Path(extra_artifacts["planner_note"]).exists():
                plan_text = Path(extra_artifacts["planner_note"]).read_text(encoding="utf-8")
            review_result = run_codex_prompt(
                build_review_prompt(task, candidate_text, plan_text=plan_text),
                args.cwd,
                review_path,
                timeout_seconds=max(20, min(args.runner_timeout, 45)),
            )
            extra_artifacts["review_stdout"] = write_text_artifact(review_stdout_path, review_result.stdout)
            extra_artifacts["review_stderr"] = write_text_artifact(review_stderr_path, review_result.stderr)
            if review_result.ok and Path(review_result.candidate_path).exists():
                extra_artifacts["review_note"] = str(Path(review_result.candidate_path).resolve())
                extra_evaluation["review_status"] = "codex-reviewer"
            else:
                extra_artifacts["review_note"] = write_text_artifact(review_path, build_review_text(task, judged, candidate_text))
                extra_evaluation["review_status"] = review_result.status
            extra_metrics["review_findings_count"] = len(judged.missing_keywords)
            extra_metrics["verifier_pass"] = judged.passed
            verifier = build_verifier_assessment(task, judged, candidate_text)
            verifier_path = ROOT / "outputs" / "verifiers" / f"{Path(args.task).stem}.md"
            extra_artifacts["verifier_report"] = write_text_artifact(
                verifier_path,
                build_verifier_report(task, judged, candidate_text),
            )
            extra_metrics["evidence_coverage"] = verifier["evidence_coverage"]
            extra_metrics["risk_flag_count"] = len(verifier["risk_flags"])
            extra_metrics["human_takeover_recommended"] = verifier["human_takeover_recommended"]
            extra_evaluation["review_mode"] = "codex-reviewer-plus-rubric"
            extra_evaluation["failure_types"] = judged.failure_types
            extra_evaluation["verifier"] = verifier

    run_path = build_run_manifest(
        args.task,
        args.workflow,
        args.out,
        candidate_text=candidate_text,
        candidate_path=candidate_path,
        mode=(
            "simulated-pipeline"
            if args.runner == "simulated_pipeline" and candidate_text
            else "codex-evaluated" if args.runner == "codex" and candidate_text else None
        ),
        status="reviewed" if args.runner in {"simulated_pipeline", "codex_pipeline"} and candidate_text else None,
        extra_metrics=extra_metrics,
        extra_artifacts=extra_artifacts,
        extra_evaluation=extra_evaluation,
    )
    print(f"Wrote benchmark manifest: {Path(run_path).resolve()}")


if __name__ == "__main__":
    main()
