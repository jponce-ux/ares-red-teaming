# Implementation Plan: ARES Rust CLI Scaffold and Workspace Baseline

**Branch**: `[003-ares-rust-cli-scaffold]` | **Date**: 2026-05-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `.specify/specs/003-ares-rust-cli-scaffold/spec.md`

## Summary

Create the initial ARES Rust CLI scaffold as a root Cargo workspace with `ares/` as the first binary crate, using `clap`, `anyhow`, and `tracing`, with module placeholders for targets, attacks, runner, evaluator, and reporting. Keep ENDI untouched and outside the Cargo workspace.

## Technical Context

**Project Scope**: ARES root Rust project
**Language/Version**: Rust stable, edition 2024 unless the local toolchain requires edition 2021 during bootstrap
**Primary Dependencies**: `clap`, `anyhow`, `tracing`, `tracing-subscriber`
**Storage**: N/A
**Testing**: `cargo fmt --all --check`; `cargo clippy --workspace --all-targets --all-features`; `cargo test --workspace`
**Target Platform**: Local CLI on developer workstation
**Project Type**: Rust Cargo workspace with `ares/` binary crate
**Performance Goals**: CLI startup and help must complete quickly enough for interactive use.
**Constraints**: No ENDI source changes; no nested `.git/`; safe Rust; no secrets.
**Scale/Scope**: Bootstrap command structure only.

## TDD plan

- **Red**: Create or update the smallest deterministic unit test before changing production code. The test MUST map to the specific FR/SC or user-story behavior being implemented.
- **Expected failure**: Run the targeted test immediately after writing it and record the failing assertion, missing symbol, or unsupported behavior before implementation starts.
- **Green**: Change only the minimum production files named by this plan and tasks to make the targeted test pass.
- **Refactor**: Refactor only after the targeted test is green, keeping the same targeted test green throughout.
- **Validation**: Run the targeted test first, then the broader feature validation command listed in `tasks.md`. A skipped or ignored test does not satisfy TDD unless the reason is documented in the task.
- **Traceability**: Each behavior-changing implementation task MUST be immediately preceded by a `[TDD-RED]` test task and an expected-failure run task, and followed by a `[TDD-GREEN]` pass-confirmation task.
- **Exact test files**: Use the concrete test file paths named by this feature `tasks.md` `[TDD-RED]` tasks; add new unit-test files there before production code when a behavior lacks coverage.

## Constitution Check

- **Defended target**: Deferred to ENDI adapter/target tickets; scaffold provides module space.
- **Attack coverage**: Deferred; scaffold only.
- **Evidence and evaluation**: Deferred; scaffold only.
- **Mitigation replay**: Deferred; scaffold only.
- **Local-first safety**: Pass; local CLI only.
- **Rust stack compliance**: Pass; Rust/Cargo first.
- **Async/concurrency safety**: No async behavior yet.
- **Rust quality gates**: Included.
- **Project boundary**: Pass; ARES only, ENDI untouched.

## Project Structure

```text
Cargo.toml
Cargo.lock
ares/
├── Cargo.toml
└── src/
    ├── main.rs
    ├── cli.rs
    ├── config.rs
    ├── targets/
    ├── attacks/
    ├── runner/
    ├── evaluator/
    └── reporting/
```

**Structure Decision**: Use a root Cargo workspace immediately with `members = ["ares"]` and `resolver = "2"`. Keep the top-level repository as the only Git repository. `endi/` remains a separate Python auxiliary project and is not a workspace member.

## Complexity Tracking

No constitution violations.
