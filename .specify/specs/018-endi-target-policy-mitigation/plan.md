# Implementation Plan: ENDI Target Policy System Prompt Mitigation

**Branch**: `[018-endi-target-policy-mitigation]` | **Date**: 2026-05-27 | **Spec**: [spec.md](spec.md)

## Summary

Add ENDI-side target policy/system prompt enforcement for mitigation replay. ENDI will accept `--system-prompt-file`, validate and load `endi/config/target_policy.md`, prepend it to provider messages before the user prompt, and fail safely when policy file validation fails.

## Technical Context

**Project Scope**: ENDI auxiliary Python project
**Language/Version**: Python `>=3.11` from `endi/pyproject.toml`
**Primary Dependencies**: Existing ENDI dependencies only; use standard library file I/O and existing pytest/ruff/mypy gates
**Storage**: `endi/config/target_policy.md`
**Testing**: Targeted pytest tests first, then `.venv/bin/python -m pytest -q`, `.venv/bin/ruff check src tests`, `.venv/bin/mypy src` from `endi/`
**Target Platform**: Local terminal runtime
**Constraints**: ENDI files only under `endi/`; no secrets; no real harmful payloads; no ARES Rust changes in this feature

## TDD plan

- **Red**: Add failing pytest tests before production code for policy message ordering, missing/empty/non-UTF-8/oversized files, JSON error shape, and policy redaction.
- **Expected failure**: Run each targeted pytest command immediately after writing the test and record the expected failure.
- **Green**: Change only `endi/src/endi/cli.py`, `endi/src/endi/providers.py` or a small ENDI policy helper module, and `endi/config/target_policy.md` as needed.
- **Refactor**: Extract helper functions only after targeted tests pass.
- **Validation**: Run targeted pytest first, then full ENDI pytest, ruff, and mypy.
- **Traceability**: Every production change must map to FR-001 through FR-008.

## Constitution Check

- **Defended target**: Pass. Adds explicit ENDI target policy/system prompt.
- **Mitigation replay**: Pass. Provides the concrete ENDI-side mitigation required before ARES replay proof.
- **Project boundary**: Pass. ENDI implementation remains under `endi/`; ARES replay remains separate.
- **Local-first safety**: Pass. No cloud infrastructure or secrets required.
- **Security defaults**: Pass. Policy content is redacted from telemetry/logs by default.
- **ENDI exception**: Python project uses ENDI gates instead of Cargo gates.

## Project Structure

```text
endi/
├── config/
│   └── target_policy.md
├── src/endi/
│   ├── cli.py
│   └── target_policy.py
└── tests/
    ├── test_cli_runtime.py
    └── test_target_policy.py
```

**Structure Decision**: Add a small `target_policy.py` helper if existing CLI/provider modules do not already provide a clean test seam. Keep policy validation independent from provider execution so validation can be unit tested without Ollama.

## Complexity Tracking

No constitution violations.
