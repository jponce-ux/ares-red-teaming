# Tasks: System Prompt Extraction Attack Category

**Project Scope**: ARES root Rust project

## Phase 1: Setup

- [ ] T001 Verify attack domain schema exists in `ares/src/attacks/`
- [ ] T002 Create system prompt extraction category module path in `ares/src/attacks/categories/`

## Phase 2: User Story 1 - Run System Prompt Extraction Variants (P1)

- [ ] T003 [P] [US1] Add fixture validation tests in `ares/tests/system_prompt_extraction_attacks.rs`
- [ ] T004 [P] [US1] Add controlled execution tests with mocked ENDI adapter in `ares/tests/system_prompt_extraction_attacks.rs`
- [ ] T005 [US1] Create three to five system prompt extraction variants in `ares/fixtures/attacks/system_prompt_extraction.jsonl`
- [ ] T006 [US1] Register system prompt extraction category loader in `ares/src/attacks/categories/system_prompt_extraction.rs`
- [ ] T007 [US1] Ensure result metadata supports evaluator leakage checks in ARES runner-compatible output

## Phase 3: Validation

- [ ] T008 Run `cargo fmt --all --check`
- [ ] T009 Run `cargo clippy --workspace --all-targets --all-features`
- [ ] T010 Run `cargo test --workspace`

## Dependencies

Requires attack schema and ENDI adapter artifacts.
