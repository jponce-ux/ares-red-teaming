# Implementation Plan: ARES Configuration and Runtime Settings

**Branch**: `[006-ares-runtime-configuration]` | **Date**: 2026-05-27 | **Spec**: [spec.md](spec.md)

## Summary

Implement typed runtime configuration loading, validation, and CLI override merging for local ARES runs against ENDI Support Assistant.

## Technical Context

**Project Scope**: ARES root Rust project
**Language/Version**: Rust stable
**Primary Dependencies**: `serde`, `toml`, `thiserror`, `clap`, `std::time::Duration`
**Storage**: Local TOML config file and safe TOML example under ARES paths
**Testing**: Unit tests for parsing, defaults, override precedence, validation failures
**Target Platform**: Local CLI
**Project Type**: Rust CLI configuration module
**Performance Goals**: Config load/validation must complete before any attack execution.
**Constraints**: No secrets in examples; typed duration/concurrency; fail fast on invalid config.
**Scale/Scope**: Runtime settings for ENDI command, provider/model/base URL, fixtures, reports, timeouts, concurrency, and evidence.

## TDD plan

- **Red**: Create or update the smallest deterministic unit test before changing production code. The test MUST map to the specific FR/SC or user-story behavior being implemented.
- **Expected failure**: Run the targeted test immediately after writing it and record the failing assertion, missing symbol, or unsupported behavior before implementation starts.
- **Green**: Change only the minimum production files named by this plan and tasks to make the targeted test pass.
- **Refactor**: Refactor only after the targeted test is green, keeping the same targeted test green throughout.
- **Validation**: Run the targeted test first, then the broader feature validation command listed in `tasks.md`. A skipped or ignored test does not satisfy TDD unless the reason is documented in the task.
- **Traceability**: Each behavior-changing implementation task MUST be immediately preceded by a `[TDD-RED]` test task and an expected-failure run task, and followed by a `[TDD-GREEN]` pass-confirmation task.
- **Exact test files**: Use the concrete test file paths named by this feature `tasks.md` `[TDD-RED]` tasks; add new unit-test files there before production code when a behavior lacks coverage.

## Constitution Check

- **Reproducible fixtures**: Config identifies fixture path.
- **Evidence/evaluation**: Config controls evidence retention safely.
- **Local-first safety**: Pass; local config, no credentials.
- **Rust stack compliance**: Pass.
- **Async/concurrency safety**: Bounded concurrency setting validated.
- **Rust quality gates**: Included.

## Project Structure

```text
ares/src/config.rs
ares/config/ares.example.toml
ares/tests/config_loading.rs
```

**Structure Decision**: Keep config types near CLI boundary, with validation reusable by runner and report modules.
The default target configuration follows `.specify/specs/017-endi-target-profile-decisions/target-profile-endi.md`.

## Complexity Tracking

No constitution violations.
