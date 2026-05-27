# Implementation Plan: Attack Runner with Bounded Concurrency and Timeouts

**Branch**: `[010-attack-runner-concurrency]` | **Date**: 2026-05-27 | **Spec**: [spec.md](spec.md)

## Summary

Implement a Tokio-based ARES attack runner that executes validated attack fixtures through the ENDI adapter with bounded concurrency, per-attack timeouts, continuation policy, structured metadata, and tracing.

## Technical Context

**Project Scope**: ARES root Rust project
**Language/Version**: Rust stable
**Primary Dependencies**: `tokio`, `futures`, `tracing`, existing config/attacks/ENDI adapter modules
**Storage**: In-memory structured results; later report/result persistence can consume them
**Testing**: Unit/integration tests for sequential, bounded concurrent, timeout, cancellation/failure continuation
**Target Platform**: Local CLI
**Performance Goals**: Concurrency must never exceed configured limit; timeout must bound every attack.
**Constraints**: No unbounded task spawning; no prompt logging unless evidence retention allows it.

## TDD plan

- **Red**: Create or update the smallest deterministic unit test before changing production code. The test MUST map to the specific FR/SC or user-story behavior being implemented.
- **Expected failure**: Run the targeted test immediately after writing it and record the failing assertion, missing symbol, or unsupported behavior before implementation starts.
- **Green**: Change only the minimum production files named by this plan and tasks to make the targeted test pass.
- **Refactor**: Refactor only after the targeted test is green, keeping the same targeted test green throughout.
- **Validation**: Run the targeted test first, then the broader feature validation command listed in `tasks.md`. A skipped or ignored test does not satisfy TDD unless the reason is documented in the task.
- **Traceability**: Each behavior-changing implementation task MUST be immediately preceded by a `[TDD-RED]` test task and an expected-failure run task, and followed by a `[TDD-GREEN]` pass-confirmation task.
- **Exact test files**: Use the concrete test file paths named by this feature `tasks.md` `[TDD-RED]` tasks; add new unit-test files there before production code when a behavior lacks coverage.

## Constitution Check

- **Attack coverage**: Executes categorized fixtures.
- **Evidence/evaluation**: Produces structured run results.
- **Mitigation replay**: Stable IDs and results support replay.
- **Local-first safety**: Pass; bounded local execution.
- **Rust stack compliance**: Pass.
- **Async/concurrency safety**: Pass; Tokio bounded concurrency/timeouts.
- **Rust quality gates**: Included.

## Project Structure

```text
ares/src/runner/mod.rs
ares/src/runner/result.rs
ares/tests/attack_runner.rs
ares/tests/runner_concurrency.rs
```

## Complexity Tracking

No constitution violations.
