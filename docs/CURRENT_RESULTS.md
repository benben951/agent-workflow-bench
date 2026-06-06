# Current Results

This document captures the current benchmark state after the first local build-out.

## What Exists Today

The project currently supports three useful result categories:

- dry-run manifests
- rubric-scored candidate outputs
- reproducible simulated planner-executor-reviewer-verifier runs
- live Codex-backed execution attempts

The most important outcome is that the project no longer stops at static prompts or README claims. It now records real execution artifacts, timing, verifier evidence coverage, and human-takeover recommendations.

## Evidence Produced

### Successful Codex-only baseline

The TAAC entry-point task was executed with a Codex-only workflow and scored successfully.

Representative run:

- `run-20260531T135516Z-2624b5da`

### Successful planner-executor-reviewer-verifier run

The TAAC entry-point task also produced a reviewed run with planner note, candidate output, review note, stdout log, stderr log, and measured latency.

Representative run:

- `run-20260531T144050Z-c7881e54`

Notable fields:

- `status = reviewed`
- `pass_rate = 1.0`
- `latency_seconds = 48.35`

### Failure and timeout evidence

The benchmark now includes failed and timed-out cases instead of only successful runs.

Representative failure:

- `run-20260531T153743Z-80bbb4ee`
- `failure_types = ["coverage_gap"]`

Representative timeout:

- `run-20260601T000044Z-37859b9b`
- both planner and runner timed out under a tight budget on the benchmark repo itself

### Reproducible simulated pipeline

The repository now includes a model-free simulated planner-executor-reviewer-verifier run. This makes the benchmark cloneable and runnable even when Codex or another live model adapter is not available.

Representative run:

- `run-20260606T181019Z-0d55ff09`

Notable fields:

- `mode = simulated-pipeline`
- `status = reviewed`
- `pass_rate = 1.0`
- `verifier_pass = true`
- `evidence_coverage = 1.0`
- `risk_flag_count = 0`
- `human_takeover_recommended = false`
- artifacts: planner note, candidate output, review note, verifier report with evidence coverage and risk flags

Public-safe sample artifacts:

- `examples/simulated_run/planner_note.md`
- `examples/simulated_run/candidate_output.md`
- `examples/simulated_run/review_note.md`
- `examples/simulated_run/verifier_report.md`
- `examples/simulated_run/run_manifest.json`
- `examples/simulated_run/summary.json`
- `examples/simulated_run/summary_report.md`

### Recruiter-readable summary report

The repository now converts run manifests into both JSON and Markdown summary artifacts:

```powershell
python scripts/summarize_results.py `
  --runs examples/simulated_run `
  --json-out examples/simulated_run/summary.json `
  --markdown-out examples/simulated_run/summary_report.md
```

Current public sample summary:

- run count: `1`
- evaluated run count: `1`
- average pass rate: `1.0`
- average latency seconds: `0.0`
- average evidence coverage: `1.0`
- human takeover recommended: `0`
- workflow: `planner-executor-reviewer-verifier-v1`
- artifact count: `6`

## Workflow Snapshot

Current workflow summary from `scripts/summarize_results.py`:

- `codex-only-v1`: evaluated runs pass rate `1.0`
- `planner-executor-reviewer-verifier-v1`: evaluated runs pass rate `0.667` after adding the reproducible simulated pipeline

This is not enough data for strong claims yet, but it is enough to show that:

- workflow variants can be compared
- success and failure are both captured
- timing, evidence coverage, risk flags, human-takeover recommendations, and artifact paths are logged
- a public-safe simulated pipeline can be reproduced without external model access

## Next Improvements

- add one more task family beyond repository explanation and due-diligence summary
- add reviewer disagreement and override fields
- compare generated Markdown reports across workflow variants
- compare Codex-only against Codex pipeline on the same task set with fixed budgets
- add more cross-task sample manifests so evidence coverage and human-takeover metrics can be compared across workflows
