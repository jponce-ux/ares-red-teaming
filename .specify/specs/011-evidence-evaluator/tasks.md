# Tasks: Evidence Capture and Rule Violation Evaluation

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

- [ ] T001 Create evaluator module files in `ares/src/evaluator/`
- [ ] T002 Verify runner result/domain types are available
- [ ] T003 [DOCS] Create deterministic evaluator heuristic matrix in `.specify/specs/011-evidence-evaluator/heuristic-matrix.md`

## Phase 2: User Story 1 - Preserve Attack Evidence (P1)

- [ ] T004 [TDD-RED] Add evidence capture tests in `ares/tests/evaluator.rs`
- [ ] T005 [TDD-GREEN] Define `EvidenceRecord` and evidence-retention behavior in `ares/src/evaluator/evidence.rs`
- [ ] T006 [TDD-GREEN] [US1] Convert runner results into evidence records in `ares/src/evaluator/evidence.rs`
- [ ] T007 [TDD-GREEN] Ensure tracing/logging redacts prompt/response unless controlled evidence output allows it

## Phase 3: User Story 2 - Evaluate Target Rule Violations (P2)

- [ ] T008 [TDD-RED] Add heuristic tests for leakage, domain escape, malicious-code assistance, refusal, partial, inconclusive, target error, and harness error in `ares/tests/evaluator.rs`
- [ ] T009 [TDD-GREEN] Define `EvaluatorDecision`/result status, `HeuristicMatch`, severity, and rationale types in `ares/src/evaluator/mod.rs`
- [ ] T010 [TDD-GREEN] Implement deterministic heuristics in `ares/src/evaluator/heuristics.rs` using `.specify/specs/011-evidence-evaluator/heuristic-matrix.md`
- [ ] T011 [TDD-GREEN] [US2] Assign severity only to `success` and `partial` results in `ares/src/evaluator/mod.rs`
- [ ] T012 [TDD-GREEN] Implement category-specific success criteria from `.specify/specs/017-endi-target-profile-decisions/evaluator-success-criteria.md`

## Phase 4: Validation

- [ ] T013 [VALIDATE] Run `cargo fmt --all --check`
- [ ] T014 [VALIDATE] Run `cargo clippy --workspace --all-targets --all-features`
- [ ] T015 [VALIDATE] Run `cargo test --workspace`

## Dependencies

Requires runner result and attack domain types.
