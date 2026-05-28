# Tasks: ENDI Target Profile and ARES MVP Decisions

**Project Scope**: Cross-project decision artifact

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


## Phase 1: Target Profile

- [x] T001 [US1] Create ENDI target profile with target name, role/domain, provider/model/base URL, allowed examples, and disallowed examples in `.specify/specs/017-endi-target-profile-decisions/target-profile-endi.md`
- [x] T002 [DOCS] Define R1_SYSTEM_PROMPT_CONFIDENTIALITY through R5_NO_FAKE_SECRETS_OR_INTERNAL_DATA in `.specify/specs/017-endi-target-profile-decisions/target-profile-endi.md`
- [x] T003 [US1] Create planned TOML target profile shape for `ares/fixtures/targets/endi_support.toml` in `.specify/specs/017-endi-target-profile-decisions/target-profile-endi.md`

## Phase 2: Evaluation and Severity

- [x] T004 [US2] Create severity rubric with Critical/High/Medium/Low/N/A criteria in `.specify/specs/017-endi-target-profile-decisions/severity-rubric.md`
- [x] T005 [DOCS] Define result statuses blocked/success/partial/inconclusive/target_error/harness_error in `.specify/specs/017-endi-target-profile-decisions/evaluator-success-criteria.md`
- [x] T006 [DOCS] Define category-specific success rules for prompt injection, jailbreak, system prompt extraction, malicious-code simulation, and out-of-domain testing in `.specify/specs/017-endi-target-profile-decisions/evaluator-success-criteria.md`

## Phase 3: Mitigation and Integration Contract

- [x] T007 [US3] Document first MVP mitigation as ENDI target policy/system prompt enforcement in `.specify/specs/017-endi-target-profile-decisions/target-profile-endi.md`
- [x] T008 [DOCS] Define ARES-to-ENDI subprocess JSON contract and required captured fields in `.specify/specs/017-endi-target-profile-decisions/ares-endi-contract.md`
- [x] T009 [US3] Document root Cargo workspace decision and implementation order in `.specify/specs/017-endi-target-profile-decisions/ares-endi-contract.md`

## Phase 4: Validation

- [x] T010 [VALIDATE] Review downstream specs 003-016 for references to these decisions

## Implementation Record

- 2026-05-27: Verified target profile, R1-R5 rules, severity rubric, evaluator success criteria, ARES-to-ENDI subprocess contract, root Cargo workspace decision, and implementation order are present and aligned with `.specify/memory/ba-pm-decisions.md`. No production code changed for this decision artifact.

