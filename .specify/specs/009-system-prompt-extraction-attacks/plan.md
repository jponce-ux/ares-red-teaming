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

## TDD plan

- **Red**: Create or update the smallest deterministic unit test before changing production code. The test MUST map to the specific FR/SC or user-story behavior being implemented.
- **Expected failure**: Run the targeted test immediately after writing it and record the failing assertion, missing symbol, or unsupported behavior before implementation starts.
- **Green**: Change only the minimum production files named by this plan and tasks to make the targeted test pass.
- **Refactor**: Refactor only after the targeted test is green, keeping the same targeted test green throughout.
- **Validation**: Run the targeted test first, then the broader feature validation command listed in `tasks.md`. A skipped or ignored test does not satisfy TDD unless the reason is documented in the task.
- **Traceability**: Each behavior-changing implementation task MUST be immediately preceded by a `[TDD-RED]` test task and an expected-failure run task, and followed by a `[TDD-GREEN]` pass-confirmation task.
- **Exact test files**: Use the concrete test file paths named by this feature `tasks.md` `[TDD-RED]` tasks; add new unit-test files there before production code when a behavior lacks coverage.

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
