# Tasks: Attack Domain Types and Fixture Schema

**Project Scope**: ARES root Rust project

## Phase 1: Setup

- [ ] T001 Add serde/thiserror dependencies to `ares/Cargo.toml`
- [ ] T002 Create `ares/src/attacks/domain.rs`, `ares/src/attacks/fixture.rs`, and `ares/src/attacks/mod.rs`

## Phase 2: User Story 1 - Load Reproducible Attack Fixtures (P1)

- [ ] T003 [P] [US1] Add fixture parsing tests in `ares/src/attacks/fixture.rs`
- [ ] T004 [US1] Implement `AttackCase`, `AttackCategory`, `TargetRule`, `ExpectedViolation`, `Severity`, `AttackId`, and `RunId` in `ares/src/attacks/domain.rs`
- [ ] T005 [US1] Implement fixture loading from JSONL or JSON in `ares/src/attacks/fixture.rs`
- [ ] T006 [US1] Add MVP fixture examples under `ares/fixtures/attacks/`

## Phase 3: User Story 2 - Reject Invalid Attack States (P2)

- [ ] T007 [P] [US2] Add validation tests for missing fields, duplicate IDs, unknown category, and unknown severity in `ares/src/attacks/fixture.rs`
- [ ] T008 [US2] Implement fixture validation errors with `thiserror` in `ares/src/attacks/fixture.rs`
- [ ] T009 [US2] Ensure invalid fixtures fail before execution in `ares/src/attacks/fixture.rs`

## Phase 4: Validation

- [ ] T010 Run `cargo fmt --all --check`
- [ ] T011 Run `cargo clippy --workspace --all-targets --all-features`
- [ ] T012 Run `cargo test --workspace`

## Dependencies

T004 before T005. T006 requires schema stability.
