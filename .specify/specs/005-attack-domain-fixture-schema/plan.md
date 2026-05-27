# Implementation Plan: Attack Domain Types and Fixture Schema

**Branch**: `[005-attack-domain-fixture-schema]` | **Date**: 2026-05-27 | **Spec**: [spec.md](spec.md)

## Summary

Define strongly typed Rust domain models and a machine-readable fixture schema for categorized ARES attacks, including MVP examples and validation before execution.

## Technical Context

**Project Scope**: ARES root Rust project
**Language/Version**: Rust stable, edition 2024/2021 per scaffold
**Primary Dependencies**: `serde`, `serde_json`, `thiserror`, `uuid` or typed string newtypes
**Storage**: Filesystem fixtures under `ares/fixtures/` or root `attacks/`
**Testing**: Unit tests for domain validation and fixture parsing
**Target Platform**: Local CLI
**Project Type**: Rust domain/fixture module
**Performance Goals**: Fixture validation must handle MVP-size files quickly and provide precise errors.
**Constraints**: Safe lab payloads only; no secrets or harmful operational payloads.
**Scale/Scope**: Core schema plus example fixtures for three MVP categories.

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
```

**Structure Decision**: Keep domain types and fixture parsing together under `attacks`, with fixtures in an ARES-owned fixture directory.

## Complexity Tracking

No constitution violations.
