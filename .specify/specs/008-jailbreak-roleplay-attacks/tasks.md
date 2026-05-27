# Tasks: Jailbreak and Role-Play Attack Category

**Project Scope**: ARES root Rust project

## Phase 1: Setup

- [ ] T001 Verify attack domain schema exists in `ares/src/attacks/`
- [ ] T002 Create jailbreak/role-play category module path in `ares/src/attacks/categories/`

## Phase 2: User Story 1 - Run Jailbreak/Role-Play Variants (P1)

- [ ] T003 [P] [US1] Add fixture validation tests in `ares/tests/jailbreak_roleplay_attacks.rs`
- [ ] T004 [P] [US1] Add controlled execution tests with mocked ENDI adapter in `ares/tests/jailbreak_roleplay_attacks.rs`
- [ ] T005 [US1] Create three to five jailbreak/role-play variants in `ares/fixtures/attacks/jailbreak_roleplay.jsonl`
- [ ] T006 [US1] Register jailbreak/role-play category loader in `ares/src/attacks/categories/jailbreak_roleplay.rs`
- [ ] T007 [US1] Ensure execution results preserve prompt, response, category, target rule, and expected violation in ARES runner-compatible output

## Phase 3: Validation

- [ ] T008 Run `cargo fmt --all --check`
- [ ] T009 Run `cargo clippy --workspace --all-targets --all-features`
- [ ] T010 Run `cargo test --workspace`

## Dependencies

Requires attack schema and ENDI adapter artifacts.
