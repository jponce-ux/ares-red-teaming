# Tasks: ARES Configuration and Runtime Settings

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

- [x] T001 Add config dependencies to `ares/Cargo.toml`
- [x] T002 Create `ares/config/ares.example.toml`

## Phase 2: User Story 1 - Load Repeatable Runtime Config (P1)

- [x] T003 [TDD-RED] Add config parsing tests in `ares/tests/config_loading.rs`
- [x] T004 [TDD-GREEN] Define `AresConfig`, `EndiCommandConfig`, `EndiTargetConfig`, `RuntimeLimits`, and `EvidenceConfig` in `ares/src/config.rs`
- [x] T005 [TDD-GREEN] Implement config file loading and defaults in `ares/src/config.rs`
- [x] T006 [TDD-GREEN] [US1] Add default ENDI MVP target settings: provider `ollama`, model `granite4.1:3b`, base URL `http://localhost:11434`, and output mode `json`
- [x] T007 [TDD-GREEN] Implement validation for paths, provider/model/base URL, timeout, concurrency, and evidence settings in `ares/src/config.rs`

## Phase 3: User Story 2 - Override Config From CLI (P2)

- [x] T008 [TDD-RED] Add override precedence tests in `ares/tests/config_loading.rs`
- [x] T009 [TDD-GREEN] [US2] Add CLI override fields to `ares/src/cli.rs`
- [x] T010 [TDD-GREEN] Implement effective config merge logic in `ares/src/config.rs`

## Phase 4: Validation

- [x] T011 [VALIDATE] Run `cargo fmt --all --check`
- [x] T012 [VALIDATE] Run `cargo clippy --workspace --all-targets --all-features`
- [x] T013 [VALIDATE] Run `cargo test --workspace`

## Implementation Record

- 2026-05-27: Added config loading under `ares/src/config/`, example TOML at `ares/config/ares.example.toml`, official ENDI target defaults, validation, and override merge logic. Red phase: `cargo test -p ares --test config_loading` first failed because `ares::config` was missing. Green phase passed after implementation. Follow-up pass migrated parsing/errors to `toml`, `serde`, and `thiserror`, including partial-section defaults and explicit validation errors. Final validation passed: `cargo fmt --all --check`, `cargo clippy --workspace --all-targets --all-features -- -D warnings`, `cargo test --workspace --all-features`.

## Dependencies

T004 before T005-T006. T008 before T009.
