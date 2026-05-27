# Ticket: Build Attack Runner with Bounded Concurrency and Timeouts

## Scope
ARES

## Context
ARES must execute attack fixtures against ENDI in a repeatable way. The runner must support local execution, bounded concurrency, cancellation, and timeouts.

Before creating Spec Kit artifacts or implementation, always read:

- `AGENTS.md`
- `.specify/memory/constitution.md`

## Goal
Implement the core ARES attack runner that executes loaded attack variants against ENDI.

## Required Spec Kit Flow

1. `$speckit-specify`
2. `$speckit-plan`
3. `$speckit-tasks`
4. `$speckit-analyze`
5. `$speckit-implement`

## Functional Requirements

- Load validated attack fixtures.
- Execute each attack against ENDI through the ENDI adapter.
- Support sequential execution.
- Support bounded concurrent execution.
- Enforce per-attack timeout.
- Capture execution metadata.
- Continue execution safely after individual attack failures when configured.
- Produce structured run results for evaluator and report generation.

## Technical Requirements

- Use Tokio.
- Use bounded concurrency, not unbounded task spawning.
- Use run IDs and attack IDs.
- Use structured tracing.
- Use typed result and error models.

## Acceptance Criteria

- ARES can execute a fixture file against ENDI.
- Timeout and process errors are represented in results.
- Concurrency is bounded by configuration.
- Tests cover sequential execution, bounded concurrency, timeout, and failure continuation.

## Validation Commands

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features
cargo test --workspace
```
