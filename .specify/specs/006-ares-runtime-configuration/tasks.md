# Tasks: ARES Configuration and Runtime Settings

**Project Scope**: ARES root Rust project

## Phase 1: Setup

- [ ] T001 Add config dependencies to `ares/Cargo.toml`
- [ ] T002 Create `ares/config/ares.example.toml`

## Phase 2: User Story 1 - Load Repeatable Runtime Config (P1)

- [ ] T003 [P] [US1] Add config parsing tests in `ares/tests/config_loading.rs`
- [ ] T004 [US1] Define `AresConfig`, `EndiCommandConfig`, `RuntimeLimits`, and `EvidenceConfig` in `ares/src/config.rs`
- [ ] T005 [US1] Implement config file loading and defaults in `ares/src/config.rs`
- [ ] T006 [US1] Implement validation for paths, timeout, concurrency, and evidence settings in `ares/src/config.rs`

## Phase 3: User Story 2 - Override Config From CLI (P2)

- [ ] T007 [P] [US2] Add override precedence tests in `ares/tests/config_loading.rs`
- [ ] T008 [US2] Add CLI override fields to `ares/src/cli.rs`
- [ ] T009 [US2] Implement effective config merge logic in `ares/src/config.rs`

## Phase 4: Validation

- [ ] T010 Run `cargo fmt --all --check`
- [ ] T011 Run `cargo clippy --workspace --all-targets --all-features`
- [ ] T012 Run `cargo test --workspace`

## Dependencies

T004 before T005-T006. T008 before T009.
