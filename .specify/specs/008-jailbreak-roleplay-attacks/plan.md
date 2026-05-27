# Implementation Plan: Jailbreak and Role-Play Attack Category

**Branch**: `[008-jailbreak-roleplay-attacks]` | **Date**: 2026-05-27 | **Spec**: [spec.md](spec.md)

## Summary

Add safe jailbreak/role-play fixtures and category registration so ARES can execute this required MVP attack category against ENDI.

## Technical Context

**Project Scope**: ARES root Rust project
**Language/Version**: Rust stable
**Primary Dependencies**: Existing attack schema, ENDI adapter, serde
**Storage**: Fixture file under `ares/fixtures/attacks/`
**Testing**: Fixture validation and controlled execution tests
**Constraints**: Safe lab-constrained prompts; no real harmful payloads.

## Constitution Check

- **Attack coverage**: Pass for jailbreak/role-play category.
- **Reproducible fixtures**: Pass.
- **Evidence/evaluation**: Result fields preserved.
- **Rust stack compliance**: Pass.

## Project Structure

```text
ares/fixtures/attacks/jailbreak_roleplay.jsonl
ares/src/attacks/categories/jailbreak_roleplay.rs
ares/tests/jailbreak_roleplay_attacks.rs
```

## Complexity Tracking

No constitution violations.
