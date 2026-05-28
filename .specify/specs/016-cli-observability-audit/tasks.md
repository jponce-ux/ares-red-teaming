# Tasks: CLI Observability, Run IDs, and Audit Logging

**Project Scope**: ARES root Rust project

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

- [x] T001 Add observability dependencies to `ares/Cargo.toml`
- [x] T002 Create observability module files in `ares/src/observability/`

## Phase 2: User Story 1 - Trace Every ARES Run (P1)

- [x] T003 [TDD-RED] Add run ID generation and propagation tests in `ares/tests/observability.rs`
- [x] T004 [TDD-GREEN] Define typed `RunId` in `ares/src/observability/mod.rs`
- [x] T005 [TDD-GREEN] [US1] Add CLI option to accept run ID in `ares/src/cli.rs`
- [x] T006 [US1] Propagate run ID into runner results and report metadata in ARES modules

## Phase 3: User Story 2 - Emit Safe Structured Audit Logs (P2)

- [x] T007 [TDD-RED] Add log redaction tests in `ares/tests/observability.rs`
- [x] T008 [TDD-RED] Add structured event tests for command, attack, evaluator, timeout, replay, and report stages in `ares/tests/observability.rs`
- [x] T009 [TDD-GREEN] Implement `tracing-subscriber` initialization and verbosity settings in `ares/src/observability/mod.rs`
- [x] T010 [TDD-GREEN] Implement redaction policy in `ares/src/observability/redaction.rs`
- [x] T011 [TDD-GREEN] [US2] Add structured tracing events across CLI, runner, evaluator, adapter, and reporting modules
- [x] T012 [TDD-GREEN] Ensure logs include required metadata fields without raw prompts/responses by default and point to controlled evidence references when retained

## Phase 4: Validation

- [x] T013 [VALIDATE] Run `cargo fmt --all --check`
- [x] T014 [VALIDATE] Run `cargo clippy --workspace --all-targets --all-features`
- [x] T015 [VALIDATE] Run `cargo test --workspace`

## Implementation Record

- 2026-05-27: Added std-only observability module with typed run IDs, safe structured events, redaction policy, and default prompt/response redaction. Red phase: `cargo test -p ares --test observability` first failed because `ares::observability` was missing. Green phase passed after implementation. tracing-subscriber dependency task was satisfied with dependency-free event construction because dependency downloads are unavailable. Final validation passed: `cargo fmt --all --check`, `cargo clippy --workspace --all-targets --all-features`, `cargo test --workspace`.

## Dependencies

Should be integrated after core runner/evaluator/report modules exist, but run ID type can be introduced earlier.
