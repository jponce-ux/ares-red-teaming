# Ticket: Add CLI Observability, Run IDs, and Audit Logging

## Scope
ARES

## Context
ARES must be auditable. Attack runs, evaluator decisions, provider calls, report generation, retries, timeouts, and concurrency limits should be traceable to a run identifier.

Before creating Spec Kit artifacts or implementation, always read:

- `AGENTS.md`
- `.specify/memory/constitution.md`

## Goal
Add structured observability and audit-friendly run metadata to ARES CLI execution.

## Required Spec Kit Flow

1. `$speckit-specify`
2. `$speckit-plan`
3. `$speckit-tasks`
4. `$speckit-analyze`
5. `$speckit-implement`

## Functional Requirements

- Generate or accept a run ID.
- Attach run ID to attack execution results.
- Attach run ID to report output.
- Emit structured tracing events.
- Include command start/end, attack start/end, evaluator decisions, timeouts, and report generation events.
- Redact secrets and sensitive values by default.
- Support configurable log verbosity.

## Technical Requirements

- Use `tracing` and `tracing-subscriber`.
- Use strongly typed run IDs.
- Avoid logging raw prompts unless evidence-retention settings allow it.
- Keep audit metadata machine-readable where practical.

## Acceptance Criteria

- Every attack run has a run ID.
- Logs include structured events for major workflow stages.
- Report includes run ID and execution metadata.
- Tests or validation cover run ID propagation.

## Validation Commands

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features
cargo test --workspace
```
