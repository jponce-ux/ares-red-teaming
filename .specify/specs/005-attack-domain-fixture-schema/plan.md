# Implementation Plan: Attack Domain Types and Fixture Schema

**Branch**: `[005-attack-domain-fixture-schema]` | **Date**: 2026-05-27 | **Spec**: [spec.md](spec.md)

## Summary

Define strongly typed Rust domain models and a machine-readable fixture schema for categorized ARES attacks, including MVP examples and validation before execution.

## Technical Context

**Project Scope**: ARES root Rust project
**Language/Version**: Rust stable, edition 2024/2021 per scaffold
**Primary Dependencies**: `serde`, `serde_json`, `thiserror`, `uuid` or typed string newtypes
**Storage**: JSONL attack fixtures under `ares/fixtures/attacks/` and TOML target fixtures under `ares/fixtures/targets/`
**Testing**: Unit tests for domain validation and fixture parsing
**Target Platform**: Local CLI
**Project Type**: Rust domain/fixture module
**Performance Goals**: Fixture validation must handle MVP-size files quickly and provide precise errors.
**Constraints**: Safe lab payloads only; no secrets or harmful operational payloads.
**Scale/Scope**: Core schema plus example fixtures for three MVP categories.

## TDD plan

- **Red**: Create or update the smallest deterministic unit test before changing production code. The test MUST map to the specific FR/SC or user-story behavior being implemented.
- **Expected failure**: Run the targeted test immediately after writing it and record the failing assertion, missing symbol, or unsupported behavior before implementation starts.
- **Green**: Change only the minimum production files named by this plan and tasks to make the targeted test pass.
- **Refactor**: Refactor only after the targeted test is green, keeping the same targeted test green throughout.
- **Validation**: Run the targeted test first, then the broader feature validation command listed in `tasks.md`. A skipped or ignored test does not satisfy TDD unless the reason is documented in the task.
- **Traceability**: Each behavior-changing implementation task MUST be immediately preceded by a `[TDD-RED]` test task and an expected-failure run task, and followed by a `[TDD-GREEN]` pass-confirmation task.
- **Exact test files**: Use the concrete test file paths named by this feature `tasks.md` `[TDD-RED]` tasks; add new unit-test files there before production code when a behavior lacks coverage.

## Constitution Check

- **Defended target**: Target rules represented explicitly.
- **Attack coverage**: Pass; MVP categories modeled.
- **Reproducible fixtures**: Pass; machine-readable fixtures.
- **Evidence/evaluation**: Provides expected violation/severity inputs.
- **Mitigation replay**: Stable IDs support replay later.
- **Rust stack compliance**: Pass.
- **Rust quality gates**: Included.

## Project Structure

```text
ares/src/attacks/domain.rs
ares/src/attacks/fixture.rs
ares/src/attacks/mod.rs
ares/fixtures/attacks/
├── prompt_injection.jsonl
├── jailbreak_roleplay.jsonl
└── system_prompt_extraction.jsonl
ares/fixtures/targets/
└── endi_support.toml
```

**Structure Decision**: Keep domain types and fixture parsing together under `attacks`, with JSONL attack fixtures in `ares/fixtures/attacks/`. The ENDI Support Assistant target profile is the official MVP target and is represented by TOML at `ares/fixtures/targets/endi_support.toml`.

## Complexity Tracking

No constitution violations.
