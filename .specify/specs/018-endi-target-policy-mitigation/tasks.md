# Tasks: ENDI Target Policy System Prompt Mitigation

**Project Scope**: ENDI auxiliary Python project. Implementation files and tests stay under `endi/`.

## TDD Execution Rules

- Every behavior-changing production task MUST follow red-green-refactor.
- Add or update a `[TDD-RED]` pytest test before changing ENDI production code.
- Run the targeted pytest command and record the expected failure before implementation.
- Implement the smallest `[TDD-GREEN]` production change needed to pass.
- Re-run the targeted pytest command and record the pass.
- Refactor only after the targeted test is green.
- Do not mark a task complete if its test was skipped, ignored, or not run unless the reason is documented.

### Required TDD task expansion

For every `[TDD-RED]` task, execution MUST include two recorded steps before any `[TDD-GREEN]` task starts: create or update the failing pytest test, then run the targeted pytest command and record the expected failure. For every `[TDD-GREEN]` task, execution MUST include the minimal production change and a targeted pytest run that confirms the behavior is green.

**Accepted TDD shorthand**: A single `[TDD-RED]` task may include both creating the failing test and running the targeted command when the task text explicitly names the target test command or the command is listed immediately after it. A single `[TDD-GREEN]` task may include both the minimal production change and the targeted pass-confirmation command when the task text explicitly says to run and confirm the targeted test. Setup, dependency, and documentation-only tasks are not requirement coverage unless a later test or validation task exercises them.

## Phase 1: Setup

- [x] T001 Verify ENDI project commands in `endi/pyproject.toml`
- [x] T002 Create `endi/config/` directory if missing

## Phase 2: Target Policy Loading and Validation

- [x] T003 [TDD-RED] Add policy loading tests for readable, missing, empty, non-UTF-8, and oversized files in `endi/tests/test_target_policy.py`
- [x] T004 [TDD-RED] Run `.venv/bin/python -m pytest tests/test_target_policy.py -q` from `endi/` and record expected policy-loading failures
- [x] T005 [TDD-GREEN] Implement minimal target policy loader and validation errors in `endi/src/endi/target_policy.py`
- [x] T006 [TDD-GREEN] Run `.venv/bin/python -m pytest tests/test_target_policy.py -q` from `endi/` and confirm policy-loading tests pass

## Phase 3: CLI Policy Option and Provider Message Ordering

- [x] T007 [TDD-RED] Add CLI/provider fake test proving `--system-prompt-file` prepends policy before user prompt in `endi/tests/test_cli_runtime.py`
- [x] T008 [TDD-RED] Run `.venv/bin/python -m pytest tests/test_cli_runtime.py::test_chat_system_prompt_file_prepends_policy -q` from `endi/` and record expected missing-option/message-ordering failure
- [x] T009 [TDD-GREEN] Add `--system-prompt-file` option to ENDI chat-compatible prompt path in `endi/src/endi/cli.py`
- [x] T010 [TDD-GREEN] Wire loaded target policy into provider message construction before the user message in `endi/src/endi/cli.py`
- [x] T011 [TDD-GREEN] Run `.venv/bin/python -m pytest tests/test_cli_runtime.py::test_chat_system_prompt_file_prepends_policy -q` from `endi/` and confirm it passes

## Phase 4: Error Shape and Redaction

- [x] T012 [TDD-RED] Add JSON-output tests for missing/invalid policy file errors without tracebacks or policy leakage in `endi/tests/test_cli_runtime.py`
- [x] T013 [TDD-RED] Run `.venv/bin/python -m pytest tests/test_cli_runtime.py::test_system_prompt_file_errors_are_structured -q` from `endi/` and record expected structured-error failure
- [x] T014 [TDD-GREEN] Return structured validation errors for policy failures in ENDI JSON and rich output paths without provider invocation
- [x] T015 [TDD-GREEN] Ensure policy content is redacted from telemetry/logging by default
- [x] T016 [TDD-GREEN] Run `.venv/bin/python -m pytest tests/test_cli_runtime.py::test_system_prompt_file_errors_are_structured -q` from `endi/` and confirm it passes

## Phase 5: Official Policy Artifact

- [x] T017 [DOCS] Create `endi/config/target_policy.md` with ENDI Support Assistant domain, R1-R5 rules, allowed examples, and disallowed examples
- [x] T018 [VALIDATE] Review `endi/config/target_policy.md` for no real secrets, real customer data, or operational harmful payloads

## Phase 6: Final Validation

- [x] T019 [VALIDATE] Run `.venv/bin/python -m pytest -q` from `endi/`
- [x] T020 [VALIDATE] Run `.venv/bin/ruff check src tests` from `endi/`
- [x] T021 [VALIDATE] Run `.venv/bin/mypy src` from `endi/`

## Implementation Record

- 2026-05-27: Added `endi.target_policy`, `--system-prompt-file` support on `chat`, `submit`, and `shell`, system-message ordering before user prompts, structured JSON validation errors, telemetry redaction for policy content, and `endi/config/target_policy.md`. Red-phase tests failed on missing module/option before implementation; targeted tests passed after implementation. Final validation from `endi/`: `.venv/bin/python -m pytest -q`, `.venv/bin/ruff check src tests`, and `.venv/bin/mypy src` all passed.

## Dependencies

T003-T006 before CLI wiring. T007-T011 before structured error/redaction tests. T017 can be done after loader validation is in place.
