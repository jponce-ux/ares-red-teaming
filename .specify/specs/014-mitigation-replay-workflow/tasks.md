# Tasks: Mitigation Replay Workflow

**Project Scope**: Cross-project integration, implemented in ARES.

## Phase 1: Setup

- [ ] T001 Create replay module files in `ares/src/replay/`
- [ ] T002 Verify runner/evaluator/report result types are available

## Phase 2: User Story 1 - Compare Baseline and Mitigated Runs (P1)

- [ ] T003 [P] [US1] Add comparison tests for closed, reduced, unchanged, regressed, missing baseline, and execution-error cases in `ares/tests/mitigation_replay.rs`
- [ ] T004 [US1] Define `ReplayBaseline`, `ReplayCandidate`, `ReplayComparison`, and `MitigationStatus` in `ares/src/replay/mod.rs`
- [ ] T005 [US1] Implement stable attack ID matching and decision comparison in `ares/src/replay/comparison.rs`
- [ ] T006 [US1] Implement result-file loading or baseline handoff in `ares/src/replay/mod.rs`

## Phase 3: User Story 2 - Include Replay in Report (P2)

- [ ] T007 [P] [US2] Add report integration test for replay statuses in `ares/tests/mitigation_replay.rs`
- [ ] T008 [US2] Expose replay comparison data to reporting module in `ares/src/replay/mod.rs`
- [ ] T009 [US2] Add replay status section to Markdown report renderer in `ares/src/reporting/markdown.rs`

## Phase 4: Validation

- [ ] T010 Run `cargo fmt --all --check`
- [ ] T011 Run `cargo clippy --workspace --all-targets --all-features`
- [ ] T012 Run `cargo test --workspace`

## Dependencies

Requires runner/evaluator/report artifacts.
