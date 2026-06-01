# Public Release Checklist

Use this checklist before publishing `agent-workflow-bench`.

## Repository hygiene

- README is clear and recruiter-readable
- LICENSE exists
- `.gitignore` excludes local artifacts and generated outputs
- no private keys, cookies, or auth files exist anywhere in the tree
- no machine-specific absolute paths remain in committed files

## Artifact hygiene

- keep only representative sample outputs if needed
- do not commit large local logs by default
- do not commit private project content from TAAC, Rogii, or employer work
- replace sensitive examples with synthetic or public-safe samples

## Technical sanity

- run `python -m compileall src scripts`
- run at least one `manifest` benchmark
- run at least one `codex-evaluated` benchmark
- run at least one failure case
- update `docs/CURRENT_RESULTS.md` if the benchmark evidence materially changes

## Story clarity

- explain why this benchmark exists
- show that it records success, failure, and timeout
- make the Codex-first baseline explicit
- keep ECC as inspiration, not as the center of the repo

## Resume fit

- the repo should support a simple claim:
  `Built a benchmark for planner-executor-reviewer agent workflows with real Codex runs, rubric scoring, timeout capture, and workflow-level comparison artifacts.`
