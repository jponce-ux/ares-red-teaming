# Implementation Plan: System Prompt Extraction Attack Category

**Branch**: `[009-system-prompt-extraction-attacks]` | **Date**: 2026-05-27 | **Spec**: [spec.md](spec.md)

## Summary

Add safe, reproducible system prompt extraction fixtures and category registration for evaluator-ready prompt leakage checks.

## Technical Context

**Project Scope**: ARES root Rust project
**Language/Version**: Rust stable
**Primary Dependencies**: Existing attack schema, ENDI adapter, serde
**Storage**: Fixture file under `ares/fixtures/attacks/`
**Testing**: Fixture validation and controlled execution tests
**Constraints**: Safe disclosure probes only; no real secrets.

## Constitution Check

- **Attack coverage**: Pass for system prompt extraction category.
- **Reproducible fixtures**: Pass.
- **Evidence/evaluation**: Leakage indicators support evaluator.
- **Rust stack compliance**: Pass.

## Project Structure

```text
ares/fixtures/attacks/system_prompt_extraction.jsonl
ares/src/attacks/categories/system_prompt_extraction.rs
ares/tests/system_prompt_extraction_attacks.rs
```

## Complexity Tracking

No constitution violations.
