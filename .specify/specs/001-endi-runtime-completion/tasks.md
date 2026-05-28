# Tasks: ENDI Runtime Completion

**Input**: Design documents from `.specify/specs/001-endi-runtime-completion/`

**Prerequisites**: plan.md, spec.md

**Project Scope**: ENDI auxiliary Python project. Spec artifacts stay under
root `.specify/specs/`. Implementation tasks use only paths under `endi/`.

**Tests**: Use ENDI Python gates from `endi/pyproject.toml`: pytest, ruff, mypy.

## TDD Execution Rules

- Every behavior-changing production task in this file MUST be executed with the red-green-refactor loop.
- Before editing production code, add or update a `[TDD-RED]` pytest unit test covering the requirement or acceptance criterion.
- Run the targeted pytest command and record the expected failure before implementation.
- Implement the smallest `[TDD-GREEN]` production change needed to pass that test.
- Re-run the targeted pytest command and record the pass before moving to the next behavior.
- Refactor only after the targeted test is green, then re-run the targeted test.
- Run broader ENDI validation at the end of each user-story phase and at final validation.
- Do not mark a task complete if its test was skipped, ignored, or not run unless the reason is documented next to the task.

### Required TDD task expansion

For every `[TDD-RED]` task, execution MUST include two recorded steps before any `[TDD-GREEN]` task starts: create or update the failing pytest test, then run the targeted pytest command and record the expected failure. For every `[TDD-GREEN]` task, execution MUST include the minimal production change and a targeted pytest run that confirms the behavior is green. If a behavior-changing task lacks an explicit `[TDD-RED]` predecessor, add that test task before implementation.

**Accepted TDD shorthand**: A single `[TDD-RED]` task may include both creating the failing test and running the targeted command when the task text explicitly names the target test command or the command is listed immediately after it. A single `[TDD-GREEN]` task may include both the minimal production change and the targeted pass-confirmation command when the task text explicitly says to run and confirm the targeted test. Setup, dependency, and documentation-only tasks are not requirement coverage unless a later test or validation task exercises them.

## Phase 1: Provider-Backed Chat

- [x] T001 [TDD-RED] [P] Add provider adapter tests for OpenAI-compatible, Anthropic-compatible, Ollama, malformed response, and missing credential cases in `endi/tests/test_provider_adapters.py`
- [x] T002 [TDD-RED] Run `.venv/bin/python -m pytest tests/test_provider_adapters.py -q` from `endi/` and record the expected provider-adapter failures
- [x] T003 [TDD-GREEN] Implement OpenAI-compatible, Anthropic-compatible, and Ollama chat adapters in `endi/src/endi/providers.py`
- [x] T004 [TDD-GREEN] Add provider selection/config helper for CLI use in `endi/src/endi/providers.py`
- [x] T005 [TDD-GREEN] Run `.venv/bin/python -m pytest tests/test_provider_adapters.py -q` from `endi/` and confirm provider adapter tests pass
- [x] T006 [TDD-RED] Add free-text submit/provider-backed chat tests in `endi/tests/test_cli_runtime.py`
- [x] T007 [TDD-RED] Run `.venv/bin/python -m pytest tests/test_cli_runtime.py::test_submit_uses_provider_backed_chat -q` from `endi/` and record the expected placeholder-response failure
- [x] T008 [TDD-GREEN] Replace placeholder free-text chat path in `endi/src/endi/cli.py` with provider-backed chat and structured failure handling
- [x] T009 [TDD-GREEN] Run `.venv/bin/python -m pytest tests/test_cli_runtime.py::test_submit_uses_provider_backed_chat -q` from `endi/` and confirm it passes

## Phase 2: Safe Built-In Tools

- [x] T010 [TDD-RED] [P] Add filesystem and shell tool tests in `endi/tests/test_builtin_tools.py`
- [x] T011 [TDD-RED] Run `.venv/bin/python -m pytest tests/test_builtin_tools.py -q` from `endi/` and record the expected missing-tool failures
- [x] T012 [TDD-GREEN] Add filesystem read/write and shell exec tool handlers in `endi/src/endi/builtin_tools.py`
- [x] T013 [TDD-GREEN] Add default built-in tool registry builder in `endi/src/endi/builtin_tools.py`
- [x] T014 [TDD-GREEN] Wire built-in tools into conversation/runtime seams without bypassing `ToolRegistry.invoke()`
- [x] T015 [TDD-GREEN] Run `.venv/bin/python -m pytest tests/test_builtin_tools.py -q` from `endi/` and confirm built-in tool tests pass

## Phase 3: CLI Controls and JSON Output

- [x] T016 [TDD-RED] [P] Add CLI behavior tests for JSON output, approve-plan context, non-interactive execution, provider options, and shell exit handling in `endi/tests/test_cli_runtime.py`
- [x] T017 [TDD-RED] Run `.venv/bin/python -m pytest tests/test_cli_runtime.py -q` from `endi/` and record the expected CLI-control failures
- [x] T018 [TDD-GREEN] Add `--output rich|json`, provider, model, local fallback, approve-plan, non-interactive, and JSON log options to `endi/src/endi/cli.py`
- [x] T019 [TDD-GREEN] Add interactive `shell` command with `/exit` and `/quit` handling in `endi/src/endi/cli.py`
- [x] T020 [TDD-GREEN] Implement stable JSON output envelope for submit results and errors in `endi/src/endi/cli.py`
- [x] T021 [TDD-GREEN] Run `.venv/bin/python -m pytest tests/test_cli_runtime.py -q` from `endi/` and confirm CLI-control tests pass

## Phase 4: Plugin Discovery and JSON Logging

- [x] T022 [TDD-RED] [P] Add plugin loader tests in `endi/tests/test_plugins.py`
- [x] T023 [TDD-RED] Add JSON Lines runtime logging tests in `endi/tests/test_cli_runtime.py`
- [x] T024 [TDD-RED] Run `.venv/bin/python -m pytest tests/test_plugins.py tests/test_cli_runtime.py -q` from `endi/` and record the expected plugin/logging failures
- [x] T025 [TDD-GREEN] Add local JSON plugin manifest loader in `endi/src/endi/plugins.py`
- [x] T026 [TDD-GREEN] Merge plugin command metadata into help/introspection output in `endi/src/endi/cli.py`
- [x] T027 [TDD-GREEN] Add JSON Lines runtime logging in `endi/src/endi/runtime_logging.py`
- [x] T028 [TDD-GREEN] Run `.venv/bin/python -m pytest tests/test_plugins.py tests/test_cli_runtime.py -q` from `endi/` and confirm plugin/logging tests pass

## Phase 5: Documentation and Validation

- [x] T029 Update `endi/MISSING_IMPLEMENTATION.md` to mark completed items and remaining backlog
- [x] T030 [VALIDATE] Run `.venv/bin/python -m pytest -q` from `endi/`
- [x] T031 [VALIDATE] Run `.venv/bin/ruff check src tests` from `endi/`
- [x] T032 [VALIDATE] Run `.venv/bin/mypy src` from `endi/`

## Dependencies & Execution Order

- Phase 1 must complete before provider-backed CLI chat is considered done.
- Phase 2 can run in parallel with Phase 1 but must complete before real tool orchestration claims.
- Phase 3 depends on Phase 1 for provider options and on Phase 4 logging APIs for log option finalization.
- Phase 4 can run in parallel with Phase 2.
- Phase 5 runs after implementation.

## Implementation Record

- 2026-05-27: Reconciled against existing ENDI implementation. Targeted provider and CLI tests were already present and passing, so no production rewrite was needed. Validation run from `endi/`: `.venv/bin/python -m pytest -q`, `.venv/bin/ruff check src tests`, and `.venv/bin/mypy src` all passed. Branch creation via `speckit-git-feature` was attempted with `GIT_BRANCH_NAME=001-endi-runtime-completion` but blocked because `.git/index.lock` is read-only in the active sandbox.

## Notes

- Do not create Python project files outside `endi/`.
- Do not add real secrets or require cloud credentials for tests.
- Keep plugin loading metadata-only; arbitrary plugin code execution is out of scope.
- Keep post-MVP graph and multi-agent templates as backlog unless explicitly requested later.
