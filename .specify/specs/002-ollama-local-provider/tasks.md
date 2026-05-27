# Tasks: Ollama Local Provider for ENDI CLI

**Input**: Design documents from `.specify/specs/002-ollama-local-provider/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-contract.md, quickstart.md

**Project Scope**: ENDI auxiliary Python project. Spec artifacts stay under root `.specify/specs/`. ENDI implementation tasks MUST use paths under `endi/`.

**Tests**: Use ENDI's Python gates from `endi/pyproject.toml`: `.venv/bin/python -m pytest -q`, `.venv/bin/ruff check src tests`, `.venv/bin/mypy src`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify existing ENDI project boundaries and current provider shape

- [x] T001 Verify ENDI Python project metadata and validation commands in `endi/pyproject.toml`
- [x] T002 Inspect current provider adapter and CLI command structure in `endi/src/endi/providers.py` and `endi/src/endi/cli.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish stable Ollama provider resolution and error categories

- [x] T003 [P] Add provider adapter tests for unqualified `ollama` provider resolution and default base URL in `endi/tests/test_provider_adapters.py`
- [x] T004 [P] Add provider adapter tests for Ollama connection failure, missing model, timeout, and malformed response categories in `endi/tests/test_provider_adapters.py`
- [x] T005 Implement unqualified Ollama provider resolution, default base URL behavior, and explicit error category mapping in `endi/src/endi/providers.py`

**Checkpoint**: Provider foundation ready for CLI stories

---

## Phase 3: User Story 1 - Chat With Local Ollama Model (Priority: P1) MVP

**Goal**: User can run a local Ollama prompt with `endi chat --provider ollama --model <model>`.

**Independent Test**: Invoke the CLI with simulated Ollama provider output and verify the selected model response is printed.

### Tests for User Story 1

- [x] T006 [P] [US1] Add CLI test for `chat` command with `--provider ollama --model llama3.2` in `endi/tests/test_cli_runtime.py`
- [x] T007 [P] [US1] Add CLI test proving `submit` remains compatible with Ollama provider options in `endi/tests/test_cli_runtime.py`

### Implementation for User Story 1

- [x] T008 [US1] Add `chat` command alias with prompt, provider, model, base URL, timeout, output, log, and plugin options in `endi/src/endi/cli.py`
- [x] T009 [US1] Ensure `submit` and `chat` share the same dispatch implementation in `endi/src/endi/cli.py`

**Checkpoint**: User Story 1 works independently

---

## Phase 4: User Story 2 - Safe Ollama Failure Handling (Priority: P2)

**Goal**: User receives clear, non-crashing feedback for Ollama connection failures, missing models, timeouts, and malformed responses.

**Independent Test**: Simulate each provider failure and verify CLI output contains a stable provider error code without traceback.

### Tests for User Story 2

- [x] T010 [P] [US2] Add CLI JSON-output failure tests for Ollama missing model and timeout paths in `endi/tests/test_cli_runtime.py`
- [x] T011 [P] [US2] Add regression test that malformed Ollama responses do not print misleading successful text in `endi/tests/test_provider_adapters.py`

### Implementation for User Story 2

- [x] T012 [US2] Normalize Ollama failure messages and details for safe CLI output in `endi/src/endi/providers.py`
- [x] T013 [US2] Preserve provider error codes in conversation output for rich and JSON CLI modes in `endi/src/endi/cli.py`

**Checkpoint**: User Story 2 works independently

---

## Phase 5: User Story 3 - Red-Team Ready Ollama CLI Contract (Priority: P3)

**Goal**: Provider/model/base URL/timeout/output options are stable and documented for later red-team orchestration.

**Independent Test**: Run quickstart commands with simulated provider behavior and verify documented command shapes work.

### Tests for User Story 3

- [x] T014 [P] [US3] Add tests for alternate Ollama base URL and timeout propagation in `endi/tests/test_provider_adapters.py`
- [x] T015 [P] [US3] Add CLI JSON success contract test for `endi chat --provider ollama --model mistral --output json` in `endi/tests/test_cli_runtime.py`

### Implementation for User Story 3

- [x] T016 [US3] Ensure CLI options for provider, model, base URL, timeout, and output are consistent between `chat`, `submit`, and `shell` in `endi/src/endi/cli.py`
- [x] T017 [US3] Update ENDI user documentation for local Ollama usage in `endi/README.md`

**Checkpoint**: User Story 3 works independently

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and task closure

- [x] T018 Run `.venv/bin/python -m pytest -q` from `endi/`
- [x] T019 Run `.venv/bin/ruff check src tests` from `endi/`
- [x] T020 Run `.venv/bin/mypy src` from `endi/`
- [x] T021 Mark all completed tasks in `.specify/specs/002-ollama-local-provider/tasks.md`
- [x] T022 [US1] Persist the last explicit provider selection for later `chat`, `submit`, and `shell` invocations in `endi/src/endi/settings.py` and `endi/src/endi/cli.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion
- **US1 (Phase 3)**: Depends on Foundational completion
- **US2 (Phase 4)**: Depends on Foundational completion and benefits from US1 shared dispatch
- **US3 (Phase 5)**: Depends on US1 and US2
- **Polish (Phase 6)**: Depends on all selected story work

### Parallel Opportunities

- T003 and T004 can be written together before T005.
- T006 and T007 can be written together before T008.
- T010 and T011 can be written together before T012.
- T014 and T015 can be written together before T016.

### Implementation Strategy

Deliver MVP first by completing T001-T009 so `endi chat --provider ollama --model <model>` works. Then complete failure categorization and JSON contract tasks before final documentation and validation.
