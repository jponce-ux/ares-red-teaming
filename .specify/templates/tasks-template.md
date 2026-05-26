---

description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Project Scope**: Tasks MUST state whether the implementation target is ARES,
ENDI, or a cross-project integration. Spec artifacts stay under root
`.specify/specs/`. ENDI implementation tasks MUST use paths under `endi/`.

**Tests**: For this Rust red teaming lab, include validation tasks for attack
parsing, target rule behavior, evaluator decisions, report generation,
mitigation replay, stress/load behavior, and async/concurrency behavior
whenever the feature touches those areas. For ENDI-scoped tasks, use ENDI's
Python gates from `endi/pyproject.toml` instead of Rust gates.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Rust Cargo workspace + target chatbot**: `Cargo.toml`, `Cargo.lock`,
  `crates/`, `attacks/`, `reports/`, and `tests/` at repository root
- **ENDI auxiliary Python project**: `endi/pyproject.toml`, `endi/src/endi/`,
  `endi/tests/`, `endi/docs/`, and ENDI-owned artifacts under `endi/`
- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

<!--
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.

  The /speckit-tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/

  Tasks MUST be organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment

  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create Cargo workspace and crate structure per implementation plan
- [ ] T002 Initialize Rust crates with Cargo dependencies and edition policy
- [ ] T003 [P] Configure rustfmt, clippy, and workspace test commands
- [ ] T003E [P] For ENDI-scoped work only, verify implementation paths stay under `endi/` and configure/use ENDI Python gates

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [ ] T004 Define target chatbot system prompt and behavior rules
- [ ] T005 [P] Create attack fixture schema for categorized prompts/templates
- [ ] T006 [P] Configure local provider settings without tracked credentials
- [ ] T007 Create strongly typed severity definitions and evaluator decision schema in crates/domain/
- [ ] T008 Configure report output structure and retained evidence format
- [ ] T009 Setup `tracing` instrumentation and typed error handling for CLI attack execution
- [ ] T010 Configure Tokio runtime boundaries, bounded concurrency, timeouts, and cancellation strategy

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Defended Chatbot Target and Manual Red Teaming (Priority: P1) 🎯 MVP

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T011 [P] [US1] Unit tests for target rule refusal behavior in crates/target-adapter/src/
- [ ] T012 [P] [US1] Integration test for manual attack transcript capture in tests/integration/

### Implementation for User Story 1

- [ ] T013 [P] [US1] Implement chatbot target adapter in crates/target-adapter/
- [ ] T014 [P] [US1] Document at least three target behavior rules in docs/
- [ ] T015 [US1] Add manual attack results table with at least five attacks in docs/
- [ ] T016 [US1] Categorize manual vulnerabilities and assign severity
- [ ] T017 [US1] Add validation and typed error handling for target interaction
- [ ] T018 [US1] Record manual-phase AI usage reflection checkpoint in docs/

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Automated Redteam CLI and Evaluation (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 2 ⚠️

- [ ] T019 [P] [US2] Unit tests for attack JSONL parsing in crates/attack-fixtures/src/
- [ ] T020 [P] [US2] Integration test for CLI attack execution in tests/integration/
- [ ] T021 [P] [US2] Evaluator decision tests in crates/evaluator/src/
- [ ] T022 [P] [US2] Async/concurrency tests for bounded attack execution in tests/async/

### Implementation for User Story 2

- [ ] T023 [P] [US2] Create prompt injection attack fixtures in attacks/
- [ ] T024 [P] [US2] Create jailbreak or role manipulation attack fixtures in attacks/
- [ ] T025 [P] [US2] Create system prompt extraction attack fixtures in attacks/
- [ ] T026 [US2] Implement redteam CLI command in crates/redteam-cli/
- [ ] T027 [US2] Implement LLM-as-judge and/or heuristic evaluator in crates/evaluator/
- [ ] T028 [US2] Persist attack results with prompt, response, decision, severity, and rationale
- [ ] T029 [US2] Add Tokio-based bounded concurrency, timeout, retry, and cancellation handling

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Report, Mitigation, and Replay Verification (Priority: P3)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 3 ⚠️

- [ ] T030 [P] [US3] Report rendering tests in crates/report/src/
- [ ] T031 [P] [US3] Mitigation replay regression test in tests/integration/
- [ ] T032 [P] [US3] Stress/load validation for replay behavior in tests/stress/

### Implementation for User Story 3

- [ ] T033 [P] [US3] Implement Markdown or HTML report renderer in crates/report/
- [ ] T034 [US3] Include executive summary, category findings, severities, successful prompts, and mitigations
- [ ] T035 [US3] Apply at least one mitigation to the chatbot target
- [ ] T036 [US3] Re-run relevant attack set and record closed, reduced, or open status
- [ ] T037 [US3] Record automated-phase AI usage reflection checkpoint in docs/

**Checkpoint**: All user stories should now be independently functional

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] TXXX [P] Documentation updates in docs/
- [ ] TXXX Code cleanup and refactoring
- [ ] TXXX Performance optimization across all stories
- [ ] TXXX [P] Additional Rust unit tests in affected crates
- [ ] TXXX Run `cargo fmt --all --check`
- [ ] TXXX Run `cargo clippy --workspace --all-targets --all-features`
- [ ] TXXX Run `cargo test --workspace`
- [ ] TXXX Security hardening
- [ ] TXXX Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation when behavior is testable
- Domain types before services
- Services before CLI commands
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Crates/modules within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit tests for target rule refusal behavior in crates/target-adapter/src/"
Task: "Integration test for manual attack transcript capture in tests/integration/"

# Launch independent Rust modules for User Story 1 together:
Task: "Implement chatbot target adapter in crates/target-adapter/"
Task: "Document target behavior rules in docs/"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Default to Rust, Cargo workspace crates, Tokio async, `tracing`, `Result`, `thiserror`, and `anyhow`
- For ENDI-scoped tasks, keep implementation under `endi/` and use ENDI Python tooling
- Keep concurrency bounded and test stress/failure paths for red teaming flows
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
