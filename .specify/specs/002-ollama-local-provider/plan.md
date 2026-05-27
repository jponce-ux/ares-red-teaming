# Implementation Plan: Ollama Local Provider for ENDI CLI

**Branch**: `[002-ollama-local-provider]` | **Date**: 2026-05-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `.specify/specs/002-ollama-local-provider/spec.md`

## Summary

ENDI must reliably route chat prompts to a locally running Ollama server when the user selects provider `ollama` and a model such as `gemma4:e2b`, `llama3.2`, or `mistral`. The implementation will extend the existing ENDI Python provider adapter and CLI command surface so unqualified provider selection (`--provider ollama --model ...`) resolves to an Ollama chat adapter, uses `http://localhost:11434` by default, exposes a `chat` command alias, and reports connection, missing-model, timeout, and malformed-response failures with explicit provider error categories.

## Technical Context

**Project Scope**: ENDI auxiliary Python project

**Language/Version**: Python >=3.11 from `endi/pyproject.toml`

**Primary Dependencies**: Existing standard-library HTTP path with `urllib.request`, Typer, Rich, prompt-toolkit, pytest, ruff, mypy

**Storage**: N/A

**Testing**: Run from `endi/`: `.venv/bin/python -m pytest -q`, `.venv/bin/ruff check src tests`, `.venv/bin/mypy src`

**Target Platform**: Local developer workstation running ENDI and optionally a local Ollama server

**Project Type**: Python CLI assistant subproject under `endi/`

**Performance Goals**: One prompt request must respect the configured timeout and never wait indefinitely; automated tests simulate network behavior without requiring a live Ollama process.

**Constraints**: ENDI implementation paths only under `endi/`; no root Python files; no tracked secrets; local Ollama default URL is `http://localhost:11434`; failure handling must be deterministic and suitable for later red-team/stress-test orchestration.

**Scale/Scope**: Single-prompt chat invocation now; stable provider contract and structured output for future multi-prompt stress execution.

## Constitution Check

- **Defended target**: Not applicable to this ENDI provider feature; ARES target chatbot requirements are not modified.
- **Attack coverage**: Not applicable to this ENDI provider feature; no attack suite is implemented here.
- **Reproducible fixtures**: Provider tests use deterministic simulated HTTP fixtures for success and failure paths.
- **Evidence and evaluation**: Structured CLI JSON output and provider error categories preserve provider outcome evidence for future orchestration.
- **Mitigation replay**: Not applicable to this ENDI provider feature.
- **Local-first safety**: Pass. Ollama execution defaults to local URL and no credentials are required or stored.
- **Report and demo readiness**: Not applicable to this ENDI provider feature.
- **Rust stack compliance**: ENDI exception applies. This feature is explicitly ENDI-scoped and uses Python under `endi/`.
- **Async and concurrency safety**: No concurrent execution is added. Timeout handling is bounded through provider request configuration.
- **Rust quality gates**: ENDI exception applies. Use ENDI Python gates from `endi/pyproject.toml`.
- **Error handling and observability**: Provider errors use `ProviderAdapterError` with explicit codes and safe details; CLI JSON output includes route/status/error envelope.
- **Project boundary**: Pass. Implementation stays under `endi/`.
- **Spec location**: Pass. Spec artifacts remain under root `.specify/specs/002-ollama-local-provider/`.
- **ENDI exception**: Pass. No Python project files are added outside `endi/`.

## Project Structure

### Documentation (this feature)

```text
.specify/specs/002-ollama-local-provider/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── cli-contract.md
└── tasks.md
```

### Source Code

```text
endi/
├── pyproject.toml
├── src/endi/
│   ├── cli.py
│   └── providers.py
└── tests/
    ├── test_cli_runtime.py
    └── test_provider_adapters.py
```

**Structure Decision**: This is an ENDI-only Python CLI feature. Provider resolution and HTTP adapter changes belong in `endi/src/endi/providers.py`; user-facing `chat` command and CLI routing behavior belong in `endi/src/endi/cli.py`; tests stay under `endi/tests/`.

## Phase 0: Research

See [research.md](research.md).

## Phase 1: Design & Contracts

See [data-model.md](data-model.md), [quickstart.md](quickstart.md), and [contracts/cli-contract.md](contracts/cli-contract.md).

## Complexity Tracking

No constitution violations or extra architectural complexity are required.
