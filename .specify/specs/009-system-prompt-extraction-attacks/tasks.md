# Tasks: System Prompt Extraction Attack Category

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

- [ ] T001 Verify attack domain schema exists in `ares/src/attacks/`
- [ ] T002 Create system prompt extraction category module path in `ares/src/attacks/categories/`

## Phase 2: User Story 1 - Run System Prompt Extraction Variants (P1)

- [ ] T003 [TDD-RED] Add fixture validation tests in `ares/tests/system_prompt_extraction_attacks.rs`
- [ ] T004 [TDD-RED] Add controlled execution tests with mocked ENDI adapter in `ares/tests/system_prompt_extraction_attacks.rs`
- [ ] T005 [US1] Create three to five system prompt extraction variants in `ares/fixtures/attacks/system_prompt_extraction.jsonl`
- [ ] T006 [TDD-GREEN] Register system prompt extraction category loader in `ares/src/attacks/categories/system_prompt_extraction.rs`
- [ ] T007 [TDD-GREEN] Ensure result metadata supports evaluator leakage checks in ARES runner-compatible output

## Phase 3: Validation

- [ ] T008 [VALIDATE] Run `cargo fmt --all --check`
- [ ] T009 [VALIDATE] Run `cargo clippy --workspace --all-targets --all-features`
- [ ] T010 [VALIDATE] Run `cargo test --workspace`

## Dependencies

Requires attack schema and ENDI adapter artifacts.
