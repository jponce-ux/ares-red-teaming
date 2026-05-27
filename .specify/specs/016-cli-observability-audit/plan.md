# Implementation Plan: CLI Observability, Run IDs, and Audit Logging

**Branch**: `[016-cli-observability-audit]` | **Date**: 2026-05-27 | **Spec**: [spec.md](spec.md)

## Summary

Add typed run IDs, structured `tracing` events, configurable verbosity, default redaction, and report/run metadata propagation across ARES CLI workflows.

## Technical Context

**Project Scope**: ARES root Rust project
**Language/Version**: Rust stable
**Primary Dependencies**: `tracing`, `tracing-subscriber`, `uuid` or typed ID generation, `serde`
**Storage**: Structured logs to stderr/file depending on config
**Testing**: Unit/integration validation for run ID propagation and redaction
**Target Platform**: Local CLI
**Constraints**: Do not log raw prompts by default; machine-readable audit fields where practical.

## TDD plan

- **Red**: Create or update the smallest deterministic unit test before changing production code. The test MUST map to the specific FR/SC or user-story behavior being implemented.
- **Expected failure**: Run the targeted test immediately after writing it and record the failing assertion, missing symbol, or unsupported behavior before implementation starts.
- **Green**: Change only the minimum production files named by this plan and tasks to make the targeted test pass.
- **Refactor**: Refactor only after the targeted test is green, keeping the same targeted test green throughout.
- **Validation**: Run the targeted test first, then the broader feature validation command listed in `tasks.md`. A skipped or ignored test does not satisfy TDD unless the reason is documented in the task.
- **Traceability**: Each behavior-changing implementation task MUST be immediately preceded by a `[TDD-RED]` test task and an expected-failure run task, and followed by a `[TDD-GREEN]` pass-confirmation task.
- **Exact test files**: Use the concrete test file paths named by this feature `tasks.md` `[TDD-RED]` tasks; add new unit-test files there before production code when a behavior lacks coverage.

## Constitution Check

- **Evidence/evaluation**: Auditability improved with run IDs.
- **Local-first safety**: Pass.
- **Logging/observability**: Pass; uses `tracing`.
- **Rust stack compliance**: Pass.
- **Rust quality gates**: Included.

## Project Structure

```text
ares/src/observability/mod.rs
ares/src/observability/redaction.rs
ares/tests/observability.rs
```

## Complexity Tracking

No constitution violations.
