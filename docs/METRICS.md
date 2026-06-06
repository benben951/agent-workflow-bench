# Metrics

## Core Metrics

- `task_completion_rate`: fraction of runs that satisfy task success criteria
- `first_pass_success_rate`: fraction of runs that pass without rerun or human takeover
- `latency_seconds`: total wall-clock time
- `cost_usd`: total estimated API cost
- `human_takeovers`: number of times a human had to intervene
- `structured_output_compliance`: whether required output schema was preserved

## Review Metrics

- `review_findings_count`: number of issues raised by the reviewer
- `review_fix_required`: whether the reviewer forced a retry
- `verifier_pass`: whether a verifier or rubric check approved the output
- `evidence_coverage`: share of task-specific verifier signals found in the candidate output
- `risk_flag_count`: number of verifier risk flags such as coverage gaps, fabricated-citation signals, or unsafe certainty
- `human_takeover_recommended`: whether the verifier recommends human review before relying on the output

## Safety Metrics

- `unsafe_action_flag`: whether the workflow proposed a risky or disallowed action
- `over_edit_flag`: whether the executor touched more files than necessary
- `trust_warnings`: list of safety or audit warnings

## Context Metrics

- `context_mode`: full, filtered, retrieved, or minimal
- `context_bytes`: serialized size of the context payload
- `retrieval_calls`: number of context retrieval operations used
