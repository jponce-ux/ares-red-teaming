# Implementation Plan: ENDI Runtime Completion

**Branch**: `001-endi-runtime-completion` | **Date**: 2026-05-26 | **Spec**: `.specify/specs/001-endi-runtime-completion/spec.md`

**Input**: Feature specification from `.specify/specs/001-endi-runtime-completion/spec.md`

## Summary

Complete ENDI's highest-impact BMAD implementation gaps by adding provider-backed
chat, concrete filesystem and shell tools, CLI operator controls, JSON output,
JSON logging, and a minimal plugin manifest loader. ENDI remains a Python
subproject under `endi/`; root Spec Kit artifacts remain under `.specify/specs/`.

## Technical Context

**Project Scope**: ENDI auxiliary Python project

**Language/Version**: Python `>=3.11` from `endi/pyproject.toml`

**Primary Dependencies**: Existing ENDI dependencies only: Typer, Rich,
Prompt Toolkit. Provider HTTP calls use Python standard library `urllib` to
avoid adding dependency churn.

**Storage**: Existing SQLite execution history remains. New JSON log sink writes
JSON Lines to configured local file paths.

**Testing**: `endi/.venv/bin/python -m pytest -q`, `endi/.venv/bin/ruff check src tests`, `endi/.venv/bin/mypy src`

**Target Platform**: Local terminal runtime.

**Project Type**: Python CLI assistant subproject under `endi/`.

**Performance Goals**: Shell commands and provider calls use explicit timeout
defaults. JSON logging is append-only and single-event per dispatch.

**Constraints**: No ENDI implementation files outside `endi/`. No real secrets
in source/tests. Provider tests must use fakes/mocks. Preserve existing public
contracts where practical.

**Scale/Scope**: Single-user local CLI runtime.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Defended target**: Not applicable to ENDI auxiliary project implementation;
  ARES red teaming target work is out of scope for this ENDI feature.
- **Attack coverage**: Not applicable to ENDI auxiliary project implementation.
- **Reproducible fixtures**: Provider, tool, plugin, and CLI tests use
  deterministic local fixtures/mocks.
- **Evidence and evaluation**: JSON output and JSON log events preserve route,
  status, output, and sanitized error metadata.
- **Mitigation replay**: Not applicable to ENDI auxiliary project implementation.
- **Local-first safety**: ENDI remains local-first; cloud providers are used
  only when explicitly configured; Ollama fallback remains explicit-only.
- **Report and demo readiness**: ENDI can demonstrate real provider-backed chat
  via fake/local provider config, safe tools, JSON output, and plugin discovery.
- **Project boundary**: Scope is ENDI. All implementation paths are under
  `endi/`; Spec Kit artifacts remain under `.specify/specs/`.
- **Spec location**: This plan lives in `.specify/specs/001-endi-runtime-completion/`.
- **ENDI exception**: Rust gates are replaced by ENDI Python gates from
  `endi/pyproject.toml`.

## Project Structure

### Documentation (this feature)

```text
.specify/specs/001-endi-runtime-completion/
├── spec.md
├── plan.md
└── tasks.md
```

### Source Code

```text
endi/
├── src/endi/
│   ├── cli.py
│   ├── providers.py
│   ├── runtime_logging.py
│   ├── builtin_tools.py
│   ├── plugins.py
│   └── routing.py
└── tests/
    ├── test_provider_adapters.py
    ├── test_builtin_tools.py
    ├── test_cli_runtime.py
    └── test_plugins.py
```

**Structure Decision**: ENDI remains a Python subproject. No files for this
feature are added to root source directories.

## Design

### Provider Adapters

Add concrete provider adapters to `endi/src/endi/providers.py`:

- `OpenAIChatProvider`
- `AnthropicChatProvider`
- `OllamaChatProvider`

Adapters expose the existing `ChatProvider.generate_reply()` protocol and use
standard-library HTTP calls. Environment variables supply credentials:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`

Ollama uses a configurable local base URL, defaulting to
`http://localhost:11434`.

### Runtime Chat Wiring

Update `endi/src/endi/cli.py` so free-text submit can call configured provider
adapters. Retain testable seams by allowing fake provider config/context at the
routing layer where existing tests already inject conversation runtime.

### Built-In Tools

Add `endi/src/endi/builtin_tools.py` with:

- filesystem read
- filesystem write
- shell exec
- default registry builder

Handlers validate paths, keep operations inside an allowed root, return
structured payloads, and rely on `ToolRegistry.invoke()` for capability checks.

### CLI Controls

Update `submit` and add `shell`:

- `--output rich|json`
- `--provider`
- `--model`
- `--local-fallback`
- `--approve-plan`
- `--non-interactive`
- `--log-json PATH`
- `shell` command with `/exit` and `/quit`

### Plugin Discovery

Add `endi/src/endi/plugins.py` with a minimal JSON manifest loader. This
feature adds command metadata discovery only, not arbitrary plugin code
execution.

### JSON Logging

Add `endi/src/endi/runtime_logging.py` that appends sanitized JSON Lines events.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| ENDI uses Python while root project is Rust | ENDI is explicitly an auxiliary Python subproject in the constitution | Migrating ENDI to Rust is outside this ENDI-scoped feature and contradicts the boundary clarification |
