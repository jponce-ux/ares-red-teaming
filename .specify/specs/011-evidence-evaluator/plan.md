# Implementation Plan: Evidence Capture and Rule Violation Evaluation

**Branch**: `[011-evidence-evaluator]` | **Date**: 2026-05-27 | **Spec**: [spec.md](spec.md)

## Summary

Implement isolated evidence capture and deterministic evaluator logic that assigns auditable result statuses, severities, rationales, and heuristic matches for attack results using the official ENDI target profile.

## Technical Context

**Project Scope**: ARES root Rust project
**Language/Version**: Rust stable
**Primary Dependencies**: `serde`, `thiserror`, `regex` or string matching, `tracing`
**Storage**: Structured in-memory evidence records for report output
**Testing**: Unit tests for each heuristic family, result status, severity rule, and execution-error case
**Target Platform**: Local CLI
**Constraints**: No uncontrolled sensitive evidence in logs; deterministic evaluator first; conservative success classification only with direct evidence.

## TDD plan

- **Red**: Create or update the smallest deterministic unit test before changing production code. The test MUST map to the specific FR/SC or user-story behavior being implemented.
- **Expected failure**: Run the targeted test immediately after writing it and record the failing assertion, missing symbol, or unsupported behavior before implementation starts.
- **Green**: Change only the minimum production files named by this plan and tasks to make the targeted test pass.
- **Refactor**: Refactor only after the targeted test is green, keeping the same targeted test green throughout.
- **Validation**: Run the targeted test first, then the broader feature validation command listed in `tasks.md`. A skipped or ignored test does not satisfy TDD unless the reason is documented in the task.
- **Traceability**: Each behavior-changing implementation task MUST be immediately preceded by a `[TDD-RED]` test task and an expected-failure run task, and followed by a `[TDD-GREEN]` pass-confirmation task.
- **Exact test files**: Use the concrete test file paths named by this feature `tasks.md` `[TDD-RED]` tasks; add new unit-test files there before production code when a behavior lacks coverage.

## Constitution Check

- **Evidence/evaluation**: Pass; core purpose.
- **Attack coverage**: Heuristics cover MVP rule classes.
- **Target profile alignment**: Uses `.specify/specs/017-endi-target-profile-decisions/`.
- **Mitigation replay**: Decisions support before/after comparison.
- **Rust stack compliance**: Pass.
- **Rust quality gates**: Included.

## Project Structure

```text
ares/src/evaluator/mod.rs
ares/src/evaluator/heuristics.rs
ares/src/evaluator/evidence.rs
ares/tests/evaluator.rs
.specify/specs/011-evidence-evaluator/heuristic-matrix.md
```

**Heuristic Matrix Decision**: Implement only deterministic heuristics listed in `heuristic-matrix.md` for MVP. Add new evaluator behavior by extending the matrix and writing failing tests first.

## Complexity Tracking

No constitution violations.
