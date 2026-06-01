# Agent Workflow Bench

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
- `codex-evaluated`: uses Codex as the executor and then scores the output

## Why It Fits This Portfolio

This project sits at the intersection of:

- agent orchestration
- LLM evaluation
- trust and safety
- workflow automation

It is a natural follow-on from `hermes-control-plane`, `llm-proxy-auditor`, and your competition evaluation work.

## Resume Angle

Built a multi-agent workflow benchmark that compares planner-executor-reviewer pipelines across coding and knowledge-work tasks using pass-rate, latency, cost, and safety-oriented run artifacts.
