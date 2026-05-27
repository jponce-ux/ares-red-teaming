# Tasks: Evidence Capture and Rule Violation Evaluation

**Project Scope**: ARES root Rust project

## Phase 1: Setup

- [ ] T001 Create evaluator module files in `ares/src/evaluator/`
- [ ] T002 Verify runner result/domain types are available

## Phase 2: User Story 1 - Preserve Attack Evidence (P1)

- [ ] T003 [P] [US1] Add evidence capture tests in `ares/tests/evaluator.rs`
- [ ] T004 [US1] Define `EvidenceRecord` and evidence-retention behavior in `ares/src/evaluator/evidence.rs`
- [ ] T005 [US1] Convert runner results into evidence records in `ares/src/evaluator/evidence.rs`
- [ ] T006 [US1] Ensure tracing/logging redacts prompt/response unless controlled evidence output allows it

## Phase 3: User Story 2 - Evaluate Target Rule Violations (P2)

- [ ] T007 [P] [US2] Add heuristic tests for leakage, domain escape, malicious-code assistance, refusal, inconclusive, and execution error in `ares/tests/evaluator.rs`
- [ ] T008 [US2] Define `EvaluatorDecision`, `HeuristicMatch`, and rationale types in `ares/src/evaluator/mod.rs`
- [ ] T009 [US2] Implement deterministic heuristics in `ares/src/evaluator/heuristics.rs`
- [ ] T010 [US2] Assign severity consistently in `ares/src/evaluator/mod.rs`

## Phase 4: Validation

- [ ] T011 Run `cargo fmt --all --check`
- [ ] T012 Run `cargo clippy --workspace --all-targets --all-features`
- [ ] T013 Run `cargo test --workspace`

## Dependencies

Requires runner result and attack domain types.
