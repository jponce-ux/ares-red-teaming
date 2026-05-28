# Tasks: Manual Attack Documentation Artifacts

**Project Scope**: ARES documentation and Spec Kit artifacts

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

- [x] T001 Verify `.specify/specs/013-manual-attack-documentation/` exists

## Phase 2: User Story 1 - Record Manual Attack Results (P1)

- [x] T002 [P] [US1] Create manual attack table template in `.specify/specs/013-manual-attack-documentation/manual-attacks.md`
- [x] T003 [US1] Add at least five safe manual attack cases with real ENDI responses across distinct categories in `.specify/specs/013-manual-attack-documentation/manual-attacks.md`
- [x] T004 [DOCS] Add required fields: ID, date/time, tester, category, attack prompt, ENDI command used, ENDI raw response, target rule under test, expected violation, observed result, decision, severity, evidence excerpt, and notes
- [x] T005 [VALIDATE] [US1] Review prompts and responses for no real secrets and no operationally harmful payloads in `.specify/specs/013-manual-attack-documentation/manual-attacks.md`
- [x] T006 [US1] Create `.specify/specs/013-manual-attack-documentation/reflection-checkpoints.md` with Reflection 1 after manual attacks and Reflection 2 after mitigation replay

## Phase 3: Validation

- [x] T007 Document whether Cargo validation is applicable for this documentation-only change
- [x] T008 [VALIDATE] Run available validation commands or record why they are not applicable
- [x] T009 [VALIDATE] Confirm no `TBD` values remain before declaring manual evidence or reflection deliverables complete

## Implementation Record

- 2026-05-27: Added `manual-attacks.md` with five safe manual ENDI commands across system prompt extraction, prompt injection, jailbreak/role-play, malicious-code simulation, and out-of-domain categories. Commands were executed for real; local Ollama was unavailable, so each observation is `target_error` with severity `N/A`. Added `reflection-checkpoints.md` with Reflection 1 and Reflection 2. Cargo validation is not applicable to this documentation-only artifact, but prompts were reviewed to avoid real secrets and operationally harmful payload detail. Confirmed no `TBD` placeholders remain.

## Dependencies

Can be done independently, but should align categories with attack schema.
