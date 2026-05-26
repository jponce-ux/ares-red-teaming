# Tasks: ENDI Runtime Completion

**Input**: Design documents from `.specify/specs/001-endi-runtime-completion/`

**Prerequisites**: plan.md, spec.md

**Project Scope**: ENDI auxiliary Python project. Spec artifacts stay under
root `.specify/specs/`. Implementation tasks use only paths under `endi/`.

**Tests**: Use ENDI Python gates from `endi/pyproject.toml`: pytest, ruff, mypy.

## Phase 1: Provider-Backed Chat

- [ ] T001 [P] Add provider adapter tests in `endi/tests/test_provider_adapters.py`
- [ ] T002 Implement OpenAI-compatible, Anthropic-compatible, and Ollama chat adapters in `endi/src/endi/providers.py`
- [ ] T003 Add provider selection/config helper for CLI use in `endi/src/endi/providers.py`
- [ ] T004 Replace placeholder free-text chat path in `endi/src/endi/cli.py` with provider-backed chat and structured failure handling

## Phase 2: Safe Built-In Tools

- [ ] T005 [P] Add filesystem and shell tool tests in `endi/tests/test_builtin_tools.py`
- [ ] T006 Add filesystem read/write and shell exec tool handlers in `endi/src/endi/builtin_tools.py`
- [ ] T007 Add default built-in tool registry builder in `endi/src/endi/builtin_tools.py`
- [ ] T008 Wire built-in tools into conversation/runtime seams without bypassing `ToolRegistry.invoke()`

## Phase 3: CLI Controls and JSON Output

- [ ] T009 [P] Add CLI behavior tests in `endi/tests/test_cli_runtime.py`
- [ ] T010 Add `--output rich|json`, provider, model, local fallback, approve-plan, non-interactive, and JSON log options to `endi/src/endi/cli.py`
- [ ] T011 Add interactive `shell` command with `/exit` and `/quit` handling in `endi/src/endi/cli.py`
- [ ] T012 Implement stable JSON output envelope for submit results and errors in `endi/src/endi/cli.py`

## Phase 4: Plugin Discovery and JSON Logging

- [ ] T013 [P] Add plugin loader tests in `endi/tests/test_plugins.py`
- [ ] T014 Add local JSON plugin manifest loader in `endi/src/endi/plugins.py`
- [ ] T015 Merge plugin command metadata into help/introspection output in `endi/src/endi/cli.py`
- [ ] T016 Add JSON Lines runtime logging in `endi/src/endi/runtime_logging.py`

## Phase 5: Documentation and Validation

- [ ] T017 Update `endi/MISSING_IMPLEMENTATION.md` to mark completed items and remaining backlog
- [ ] T018 Run `endi/.venv/bin/python -m pytest -q`
- [ ] T019 Run `endi/.venv/bin/ruff check src tests`
- [ ] T020 Run `endi/.venv/bin/mypy src`

## Dependencies & Execution Order

- Phase 1 must complete before provider-backed CLI chat is considered done.
- Phase 2 can run in parallel with Phase 1 but must complete before real tool orchestration claims.
- Phase 3 depends on Phase 1 for provider options and on Phase 4 logging APIs for log option finalization.
- Phase 4 can run in parallel with Phase 2.
- Phase 5 runs after implementation.

## Notes

- Do not create Python project files outside `endi/`.
- Do not add real secrets or require cloud credentials for tests.
- Keep plugin loading metadata-only; arbitrary plugin code execution is out of scope.
- Keep post-MVP graph and multi-agent templates as backlog unless explicitly requested later.
