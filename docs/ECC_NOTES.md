# ECC Notes for Agent Workflow Bench

These notes capture the parts of `affaan-m/ECC` that are worth borrowing into
this project.

## What ECC Gets Right

ECC treats agent work as an operating system rather than a single prompt pack.

The strongest reusable ideas are:

- harness-native structure instead of one agent-specific hack
- explicit roles, commands, rules, hooks, and skills
- memory and context discipline instead of unlimited transcript sprawl
- security checks before claiming a workflow is production-ready
- verification and review as first-class workflow stages

## What We Should Borrow

### 1. Workflow roles are first-class

Our benchmark should not compare "model A vs model B" only.
It should compare role layouts such as:

- planner -> executor -> reviewer
- executor only
- executor -> verifier
- planner -> executor -> reviewer -> verifier

### 2. Context discipline matters

ECC emphasizes selective loading and avoiding wasteful context growth.

For us, that means recording:

- what context each role received
- whether context was full, filtered, or retrieved
- whether extra context improved or hurt pass rate

### 3. Verification must be benchmarked

ECC treats review and guardrails as part of the system.

For us, verification should not be a vague note.
It should be measured:

- how often a reviewer catches a bad answer
- whether a verifier improves first-pass success
- whether safety checks add useful signal or only cost

### 4. Cross-harness comparison is valuable

ECC works across Claude Code, Codex, Cursor, and others.

That suggests our benchmark should be harness-aware, not only model-aware.

Useful comparison dimensions:

- Codex executor vs Claude executor
- Claude reviewer vs rubric reviewer
- single-harness vs mixed-harness workflows

### 5. Security and trust are not optional

ECC includes hardening and security instincts.

For our benchmark, this should become:

- structured-output compliance checks
- unsafe-edit or over-edit tracking
- human takeover logging
- trust score or safety flags in each run manifest

## What We Should Not Copy Blindly

- Huge command and plugin sprawl before we have benchmark evidence
- Harness-specific customization that makes the benchmark harder to compare
- Fancy orchestration before the task catalog and metrics are stable

## Practical Conclusion

ECC is a strong inspiration for system shape.
Our project should stay smaller and more evaluation-first:

- fewer moving parts
- clearer metrics
- more comparable runs
- stronger evidence about whether multi-agent workflows help at all
