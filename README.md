# Agent Workflow Bench

[![CI](https://github.com/benben951/agent-workflow-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/benben951/agent-workflow-bench/actions/workflows/ci.yml)

Benchmark planner-executor-reviewer agent workflows on real coding and knowledge-work tasks.

## Why This Project Is Worth Building

Single-agent demos are easy to find. What is still missing is a practical way to answer questions like:

- when does a multi-agent pipeline outperform a single strong model?
- which planner or reviewer combinations improve pass rate instead of just adding cost?
- how often do agents drift, over-edit, stall, or require human takeover?
- which workflow is safest for high-stakes domains such as coding, risk review, or compliance analysis?

This project turns "multi-agent is a trend" into something measurable.

## Current Scope

This repository is an evaluation-first scaffold for benchmarking agent workflows.

- It defines task specs and workflow specs.
- It produces structured run manifests in JSON.
- It is designed to compare workflows across cost, latency, quality, and safety.
- The current implementation is a dry-run baseline that creates reproducible run artifacts before real agent adapters are added.
- It is influenced by operating-system-style agent stacks such as ECC, but stays intentionally smaller and more benchmark-first.
- It now supports simple rubric scoring against candidate output files, so runs can move beyond pure dry-run manifests.
- It now includes a reproducible simulated planner-executor-reviewer-verifier pipeline that generates reviewable artifacts without requiring external model access.

## Core Idea

Each run uses explicit roles:

```text
planner -> executor -> reviewer -> optional verifier
```

The system records:

- task type
- agents assigned to each role
- prompts and routing policy
- artifact paths
- pass or fail against a task-specific rubric
- latency and cost placeholders
- human takeover count

## ECC-Inspired Design Principles

This project borrows the strongest structural ideas from `affaan-m/ECC` without copying its full surface area:

- explicit workflow roles instead of one giant prompt
- context discipline instead of unlimited transcript sprawl
- verification as a benchmarked stage, not a vague afterthought
- cross-harness comparison instead of single-agent tunnel vision
- safety and trust fields in every run artifact

Notes: [docs/ECC_NOTES.md](docs/ECC_NOTES.md)

Current evidence snapshot: [docs/CURRENT_RESULTS.md](docs/CURRENT_RESULTS.md)

## Quick Start

```powershell
cd agent-workflow-bench
python scripts/run_benchmark.py `
  --task tasks/coding/repo_navigation.json `
  --workflow workflows/default.json `
  --out outputs/runs
```

The command writes a timestamped JSON manifest under `outputs/runs/`.

Additional workflow variants:

```powershell
python scripts/run_benchmark.py `
  --task tasks/docs/due_diligence_summary.json `
  --workflow workflows/planner_executor_reviewer_verifier.json `
  --out outputs/runs
```

Evaluate a candidate answer with the built-in rubric judge:

```powershell
python scripts/run_benchmark.py `
  --task tasks/docs/due_diligence_summary.json `
  --workflow workflows/planner_executor_reviewer_verifier.json `
  --candidate-file examples/due_diligence_answer.txt `
  --out outputs/runs
```

Try a failing sample on purpose:

```powershell
python scripts/run_benchmark.py `
  --task tasks/docs/due_diligence_summary.json `
  --workflow workflows/planner_executor_reviewer_verifier.json `
  --candidate-file examples/due_diligence_bad_answer.txt `
  --out outputs/runs
```

Run the reproducible simulated multi-agent pipeline:

```powershell
python scripts/run_benchmark.py `
  --task tasks/docs/due_diligence_summary.json `
  --workflow workflows/planner_executor_reviewer_verifier.json `
  --runner simulated_pipeline `
  --out outputs/runs
```

This writes a manifest plus four reviewable artifacts:

- planner note
- candidate output
- reviewer note
- verifier report

Public-safe sample artifacts are committed under [examples/simulated_run](examples/simulated_run).

Generate a recruiter-readable summary report from run manifests:

```powershell
python scripts/summarize_results.py `
  --runs examples/simulated_run `
  --json-out examples/simulated_run/summary.json `
  --markdown-out examples/simulated_run/summary_report.md
```

Sample report: [examples/simulated_run/summary_report.md](examples/simulated_run/summary_report.md)

## Suggested Task Families

- coding bugfix tasks
- repo navigation and architecture explanation tasks
- document QA or due-diligence summarization tasks
- browser or tool-using workflow tasks

## Workflow Variants

- `workflows/default.json`: planner, executor, reviewer
- `workflows/codex_only.json`: single-agent baseline
- `workflows/planner_executor_reviewer_verifier.json`: full pipeline with a verifier role

## Current Execution Modes

- `dry-run`: generates a manifest and records the intended workflow
- `evaluated`: scores a candidate output file against task-specific rubric keywords
- `simulated-pipeline`: generates planner, executor, reviewer, and verifier artifacts without external model access
- `codex-evaluated`: uses Codex as the executor and then scores the output
- `reported`: summarizes run manifests into JSON and Markdown reports for workflow comparison

## Why It Fits This Portfolio

This project sits at the intersection of:

- agent orchestration
- LLM evaluation
- trust and safety
- workflow automation

It is a natural follow-on from `hermes-control-plane`, `llm-proxy-auditor`, and your competition evaluation work.

## Resume Angle

Built a multi-agent workflow benchmark that compares planner-executor-reviewer-verifier pipelines across coding and knowledge-work tasks using pass-rate, latency, failure taxonomy, verifier artifacts, summary JSON, and recruiter-readable Markdown reports.
