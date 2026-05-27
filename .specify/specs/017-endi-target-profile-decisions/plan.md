# Implementation Plan: ENDI Target Profile and ARES MVP Decisions

**Branch**: `[017-endi-target-profile-decisions]` | **Date**: 2026-05-27 | **Spec**: [spec.md](spec.md)

## Summary

Record the BA/PM product decisions that unblock ARES implementation: ENDI is the official target, target rules R1-R5 are canonical, result statuses and severity rubric are fixed, first mitigation is ENDI target policy enforcement, ARES uses a root Cargo workspace, and ARES calls ENDI only through subprocess CLI JSON output.

## Technical Context

**Project Scope**: Cross-project decision artifact
**Language/Version**: Rust for ARES; Python remains isolated under ENDI
**Primary Dependencies**: N/A for the decision artifact; downstream ARES specs use Cargo/Tokio/tracing and ENDI specs use Python gates
**Storage**: Markdown/TOML target-profile artifacts under this feature folder and future `ares/fixtures/targets/`
**Testing**: Reviewable artifacts; downstream implementation tests consume these decisions
**Target Platform**: Local CLI
**Project Type**: Spec Kit decision artifact that governs ARES and ENDI integration
**Constraints**: ARES must not import ENDI Python code; ENDI behavior changes stay under `endi/`; no real secrets or operationally harmful payloads.

## TDD plan

- **Red**: Create or update the smallest deterministic unit test before changing production code. The test MUST map to the specific FR/SC or user-story behavior being implemented.
- **Expected failure**: Run the targeted test immediately after writing it and record the failing assertion, missing symbol, or unsupported behavior before implementation starts.
- **Green**: Change only the minimum production files named by this plan and tasks to make the targeted test pass.
- **Refactor**: Refactor only after the targeted test is green, keeping the same targeted test green throughout.
- **Validation**: Run the targeted test first, then the broader feature validation command listed in `tasks.md`. A skipped or ignored test does not satisfy TDD unless the reason is documented in the task.
- **Traceability**: Each behavior-changing implementation task MUST be immediately preceded by a `[TDD-RED]` test task and an expected-failure run task, and followed by a `[TDD-GREEN]` pass-confirmation task.
- **Exact test files**: Use the concrete test file paths named by this feature `tasks.md` `[TDD-RED]` tasks; add new unit-test files there before production code when a behavior lacks coverage.

## Constitution Check

- **Defended target**: Pass. Defines ENDI Support Assistant target profile and R1-R5.
- **Attack coverage**: Pass. Defines categories and rules that attack fixtures must cover.
- **Reproducible fixtures**: Pass. Provides target rule IDs for fixtures.
- **Evidence and evaluation**: Pass. Defines statuses, severity, and conservative success criteria.
- **Mitigation replay**: Pass. Defines concrete ENDI target-policy mitigation and ARES replay ownership.
- **Local-first safety**: Pass. Ollama local target config.
- **Rust stack compliance**: Pass. Root Cargo workspace plus `ares/` binary crate.
- **Project boundary**: Pass. ARES subprocesses ENDI; ENDI owns target policy behavior.

## Project Structure

```text
.specify/specs/017-endi-target-profile-decisions/
├── spec.md
├── plan.md
├── tasks.md
├── target-profile-endi.md
├── severity-rubric.md
├── evaluator-success-criteria.md
└── ares-endi-contract.md
```

## Complexity Tracking

No constitution violations.
