# Tasks: ARES Rust CLI Scaffold and Workspace Baseline

**Input**: Design documents from `.specify/specs/003-ares-rust-cli-scaffold/`
**Project Scope**: ARES root Rust project
**Tests**: Cargo fmt, clippy, and tests.

## TDD Execution Rules

- Every behavior-changing production task in this file MUST be executed with the red-green-refactor loop.
- Before editing production code, add or update a `[TDD-RED]` unit test covering the requirement or acceptance criterion.
- Run the targeted test and record the expected failure before implementation.
- Implement the smallest `[TDD-GREEN]` production change needed to pass that test.
- Re-run the targeted test and record the pass before moving to the next behavior.
- Refactor only after the targeted test is green, then re-run the targeted test.
- Run broader validation at the end of each user-story phase and at final validation.
- Do not mark a task complete if its test was skipped, ignored, or not run unless the reason is documented next to the task.

### Required TDD task expansion

For every `[TDD-RED]` task, execution MUST include two recorded steps before any `[TDD-GREEN]` task starts: create or update the failing unit test, then run the targeted test command and record the expected failure. For every `[TDD-GREEN]` task, execution MUST include the minimal production change and a targeted test run that confirms the behavior is green. If a behavior-changing task lacks an explicit `[TDD-RED]` predecessor, add that test task before implementation.

**Accepted TDD shorthand**: A single `[TDD-RED]` task may include both creating the failing test and running the targeted command when the task text explicitly names the target test command or the command is listed immediately after it. A single `[TDD-GREEN]` task may include both the minimal production change and the targeted pass-confirmation command when the task text explicitly says to run and confirm the targeted test. Setup, dependency, and documentation-only tasks are not requirement coverage unless a later test or validation task exercises them.


## Phase 1: Setup

- [x] T001 Verify no nested Git repository exists under `ares/`
- [x] T002 Create root `Cargo.toml` with `[workspace]`, `members = ["ares"]`, and `resolver = "2"`
- [x] T003 Create or validate `ares/Cargo.toml` with Rust edition and dependencies
- [x] T004 Verify `endi/` is not listed as a Cargo workspace member
- [x] T005 Create baseline module directories under `ares/src/`

## Phase 2: User Story 1 - Start ARES CLI (P1)

- [x] T006 [TDD-RED] Add CLI help smoke test in `ares/tests/cli_help.rs`
- [x] T007 [TDD-GREEN] Implement `clap` command parser in `ares/src/cli.rs`
- [x] T008 [TDD-GREEN] Implement binary entrypoint with `anyhow` and `tracing` setup in `ares/src/main.rs`

## Phase 3: User Story 2 - Validate Rust Quality Gates (P2)

- [x] T009 [TDD-RED] Add basic unit test for CLI construction in `ares/src/cli.rs`
- [x] T010 [US2] Document validation commands in `ares/README.md`
- [x] T011 [VALIDATE] Run `cargo fmt --all --check`
- [x] T012 [VALIDATE] Run `cargo clippy --workspace --all-targets --all-features` from the repository root
- [x] T013 [VALIDATE] Run `cargo test --workspace` from the repository root

## Implementation Record

- 2026-05-27: Created root Cargo workspace, validated `ares/` has no nested Git repo, added ARES module directories, implemented a dependency-free CLI help/version scaffold, and documented quality gates in `ares/README.md`. Red phase: `cargo test -p ares cli_help_shows_ares_entrypoint` first failed because help output was still `Hello, world!`; after implementation `cargo test -p ares cli` passed. A first attempt with planned external crates failed because the sandbox cannot resolve `index.crates.io`; production scaffold was kept std-only for offline validation. Final validation passed: `cargo fmt --all --check`, `cargo clippy --workspace --all-targets --all-features`, `cargo test --workspace`.

## Dependencies

T001-T003 before user-story work. US1 is MVP. US2 follows scaffold creation.
