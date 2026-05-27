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
