# Tasks: Attack Domain Types and Fixture Schema

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

- [ ] T001 Add serde/thiserror dependencies to `ares/Cargo.toml`
- [ ] T002 Create `ares/src/attacks/domain.rs`, `ares/src/attacks/fixture.rs`, and `ares/src/attacks/mod.rs`

## Phase 2: User Story 1 - Load Reproducible Attack Fixtures (P1)

- [ ] T003 [TDD-RED] Add fixture parsing tests in `ares/src/attacks/fixture.rs`
- [ ] T004 [TDD-GREEN] Implement `AttackCase`, `AttackCategory`, `TargetRule`, `ExpectedViolation`, `Severity`, `ResultStatus`, `AttackId`, and `RunId` in `ares/src/attacks/domain.rs`
- [ ] T005 [TDD-GREEN] Implement fixture loading from JSONL only in `ares/src/attacks/fixture.rs`
- [ ] T006 [US1] Add MVP fixture examples under `ares/fixtures/attacks/`
- [ ] T007 [US1] Add `ares/fixtures/targets/endi_support.toml` with provider `ollama`, model `granite4.1:3b`, base URL `http://localhost:11434`, and R1-R5 target rules

## Phase 3: User Story 2 - Reject Invalid Attack States (P2)

- [ ] T008 [TDD-RED] Add validation tests for missing fields, duplicate IDs, unknown category, and unknown severity in `ares/src/attacks/fixture.rs`
- [ ] T009 [TDD-RED] Add validation tests for unknown ENDI target rule and invalid result status in `ares/src/attacks/fixture.rs`
- [ ] T010 [TDD-GREEN] Implement fixture validation errors with `thiserror` in `ares/src/attacks/fixture.rs`
- [ ] T011 [TDD-GREEN] Ensure invalid fixtures fail before execution in `ares/src/attacks/fixture.rs`

## Phase 4: Validation

- [ ] T012 [VALIDATE] Run `cargo fmt --all --check`
- [ ] T013 [VALIDATE] Run `cargo clippy --workspace --all-targets --all-features`
- [ ] T014 [VALIDATE] Run `cargo test --workspace`

## Dependencies

T004 before T005. T006 requires schema stability.
