# v0.1 Release Notes

Agent Workflow Bench v0.1 is a compact benchmark-first scaffold for planner-executor-reviewer-verifier workflows.

## Highlights

- Task specs and workflow specs as JSON.
- Dry-run, rubric-evaluated, and simulated-pipeline execution modes.
- Planner, executor, reviewer, and verifier artifacts without external model access.
- Evidence coverage, risk flags, pass-rate, and human-takeover fields.
- Markdown and JSON summary reports.
- Public-safe passing and failing examples.

## Good First Review Path

1. Read `examples/simulated_run/summary_report.md`.
2. Compare `examples/failing_run` with `examples/simulated_run`.
3. Run the simulated-pipeline quickstart from `README.md`.
4. Run `python -m pytest -q`.

## Boundary

This release is evaluation-first. Live model adapters are intentionally separated from the reproducible simulated baseline.
