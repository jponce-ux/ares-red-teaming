# Tasks: ENDI CLI Command Adapter

**Project Scope**: Cross-project integration; Rust implementation in ARES only.

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

- [x] T001 Verify existing ARES scaffold paths in `ares/src/`
- [x] T002 Add Tokio process/test dependencies to `ares/Cargo.toml`

## Phase 2: Foundation

- [x] T003 [SETUP] Define `EndiExecutionConfig` in `ares/src/targets/endi.rs`
- [x] T004 [SETUP] Define `EndiCommandResult` and `EndiCommandError` in `ares/src/targets/endi.rs`
- [x] T005 [SETUP] Define typed parsed ENDI JSON envelope fields in `ares/src/targets/endi.rs`

## Phase 3: User Story 1 - Send Prompt Through ENDI (P1)

- [x] T006 [TDD-RED] Add success integration test in `ares/tests/endi_adapter.rs`
- [x] T007 [TDD-GREEN] Implement `EndiClient::chat` with structured arguments in `ares/src/targets/endi.rs`
- [x] T008 [TDD-GREEN] Implement `EndiClient::version`, `EndiClient::submit`, and `EndiClient::validate_environment` in `ares/src/targets/endi.rs`
- [x] T009 [TDD-GREEN] [US1] Capture command, stdout, stderr, exit status, started time, duration, timeout, and parsed ENDI output in `ares/src/targets/endi.rs`
- [x] T010 [TDD-GREEN] [US1] Default attack execution options to provider `ollama`, model `granite4.1:3b`, base URL `http://localhost:11434`, timeout 60 seconds, and `--output json`

## Phase 4: User Story 2 - Bound ENDI Process Execution (P2)

- [x] T011 [TDD-RED] Add tests for missing command, non-zero exit, and timeout in `ares/tests/endi_adapter.rs`
- [x] T012 [TDD-GREEN] Implement timeout handling with `tokio::time::timeout` in `ares/src/targets/endi.rs`
- [x] T013 [TDD-GREEN] [US2] Add `tracing` spans/events with prompt redaction in `ares/src/targets/endi.rs`

## Phase 5: Validation

- [x] T014 [VALIDATE] Run `cargo fmt --all --check`
- [x] T015 [VALIDATE] Run `cargo clippy --workspace --all-targets --all-features`
- [x] T016 [VALIDATE] Run `cargo test --workspace`

## Implementation Record

- 2026-05-27: Added `ares::targets::endi` with `EndiClient`, execution config, command result, parsed ENDI JSON envelope fields, environment validation, chat/submit/version methods, stdout/stderr/exit/duration/timeout capture, and default Ollama granite4.1:3b options. Red phase: `cargo test -p ares --test endi_adapter` first failed because the public module was missing. Green phase passed after implementation. Follow-up pass migrated the adapter to `tokio::process`, Tokio timeout handling, `thiserror`, `serde_json`, and prompt-redacted `tracing` instrumentation. Final validation passed: `cargo fmt --all --check`, `cargo clippy --workspace --all-targets --all-features -- -D warnings`, `cargo test --workspace --all-features`.

## Dependencies

T003-T004 before adapter implementation. Tests precede implementation per story.
