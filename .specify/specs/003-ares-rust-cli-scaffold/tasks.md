# Tasks: ARES Rust CLI Scaffold and Workspace Baseline

**Input**: Design documents from `.specify/specs/003-ares-rust-cli-scaffold/`
**Project Scope**: ARES root Rust project
**Tests**: Cargo fmt, clippy, and tests.

## Phase 1: Setup

- [ ] T001 Verify no nested Git repository exists under `ares/`
- [ ] T002 Create or validate `ares/Cargo.toml` with Rust edition and dependencies
- [ ] T003 Create baseline module directories under `ares/src/`

## Phase 2: User Story 1 - Start ARES CLI (P1)

- [ ] T004 [P] [US1] Add CLI help smoke test in `ares/tests/cli_help.rs`
- [ ] T005 [US1] Implement `clap` command parser in `ares/src/cli.rs`
- [ ] T006 [US1] Implement binary entrypoint with `anyhow` and `tracing` setup in `ares/src/main.rs`

## Phase 3: User Story 2 - Validate Rust Quality Gates (P2)

- [ ] T007 [P] [US2] Add basic unit test for CLI construction in `ares/src/cli.rs`
- [ ] T008 [US2] Document validation commands in `ares/README.md`
- [ ] T009 [US2] Run `cargo fmt --all --check`
- [ ] T010 [US2] Run `cargo clippy --workspace --all-targets --all-features`
- [ ] T011 [US2] Run `cargo test --workspace`

## Dependencies

T001-T003 before user-story work. US1 is MVP. US2 follows scaffold creation.
