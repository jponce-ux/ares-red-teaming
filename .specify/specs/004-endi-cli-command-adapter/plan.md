# Implementation Plan: ENDI CLI Command Adapter

**Branch**: `[004-endi-cli-command-adapter]` | **Date**: 2026-05-27 | **Spec**: [spec.md](spec.md)

## Summary

Implement an ARES-side Rust adapter that invokes ENDI Support Assistant using structured process arguments, captures stdout/stderr/exit/duration/parsed JSON metadata, enforces timeouts, and returns typed results/errors without changing ENDI.

## Technical Context

**Project Scope**: Cross-project integration
**Language/Version**: Rust stable, edition 2024 unless existing scaffold uses 2021
**Primary Dependencies**: `tokio`, `thiserror`, `tracing`, `serde` if result serialization is needed
**Storage**: N/A
**Testing**: Cargo fmt, clippy, unit/integration tests with controlled commands
**Target Platform**: Local CLI
**Project Type**: ARES Rust CLI module
**Performance Goals**: Adapter respects configured timeout for every process call.
**Constraints**: Do not modify ENDI; no shell interpolation; redact prompt in logs unless retained as evidence; do not import ENDI Python code.
**Scale/Scope**: Single command execution API for later runner use.

## TDD plan

- **Red**: Create or update the smallest deterministic unit test before changing production code. The test MUST map to the specific FR/SC or user-story behavior being implemented.
- **Expected failure**: Run the targeted test immediately after writing it and record the failing assertion, missing symbol, or unsupported behavior before implementation starts.
- **Green**: Change only the minimum production files named by this plan and tasks to make the targeted test pass.
- **Refactor**: Refactor only after the targeted test is green, keeping the same targeted test green throughout.
- **Validation**: Run the targeted test first, then the broader feature validation command listed in `tasks.md`. A skipped or ignored test does not satisfy TDD unless the reason is documented in the task.
- **Traceability**: Each behavior-changing implementation task MUST be immediately preceded by a `[TDD-RED]` test task and an expected-failure run task, and followed by a `[TDD-GREEN]` pass-confirmation task.
- **Exact test files**: Use the concrete test file paths named by this feature `tasks.md` `[TDD-RED]` tasks; add new unit-test files there before production code when a behavior lacks coverage.

## Constitution Check

- **Defended target**: Adapter enables ENDI target interaction.
- **Attack coverage**: Deferred to category tickets.
- **Evidence and evaluation**: Captures output metadata for later evidence.
- **Mitigation replay**: Deferred.
- **Local-first safety**: Pass; local process execution.
- **Rust stack compliance**: Pass.
- **Async/concurrency safety**: Uses Tokio process and timeout.
- **Rust quality gates**: Included.
- **Project boundary**: Pass; ARES calls ENDI, ENDI source unchanged.

## Project Structure

```text
ares/src/targets/endi.rs
ares/src/targets/mod.rs
ares/tests/endi_adapter.rs
```

**Structure Decision**: Place ENDI process integration under ARES target adapter modules. The MVP command defaults to `cd endi` followed by `.venv/bin/python -m endi.cli chat "<attack prompt>" --provider ollama --model granite4.1:3b --base-url http://localhost:11434 --timeout-seconds 60 --output json --non-interactive`. The adapter contract is governed by `.specify/specs/017-endi-target-profile-decisions/ares-endi-contract.md`.

## Complexity Tracking

No constitution violations.
