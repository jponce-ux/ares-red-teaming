# Implementation Plan: Mitigation Replay Workflow

**Branch**: `[014-mitigation-replay-workflow]` | **Date**: 2026-05-27 | **Spec**: [spec.md](spec.md)

## Summary

Implement ARES replay comparison logic that can load baseline results, run or load post-mitigation results after the ENDI-side target policy mitigation from `.specify/specs/018-endi-target-policy-mitigation/`, classify mitigation outcomes by stable attack ID, and feed replay status into reports.

## Technical Context

**Project Scope**: Cross-project integration
**Language/Version**: Rust stable
**Primary Dependencies**: `serde`, existing runner/evaluator/report modules, `thiserror`
**Storage**: Structured result files and replay comparison output
**Testing**: Unit tests for comparison and report integration tests
**Target Platform**: Local CLI
**Constraints**: Stable attack IDs required; safely handle missing/malformed result files; ENDI mitigation implementation remains isolated in `.specify/specs/018-endi-target-policy-mitigation/` and under `endi/`.

## TDD plan

- **Red**: Create or update the smallest deterministic unit test before changing production code. The test MUST map to the specific FR/SC or user-story behavior being implemented.
- **Expected failure**: Run the targeted test immediately after writing it and record the failing assertion, missing symbol, or unsupported behavior before implementation starts.
- **Green**: Change only the minimum production files named by this plan and tasks to make the targeted test pass.
- **Refactor**: Refactor only after the targeted test is green, keeping the same targeted test green throughout.
- **Validation**: Run the targeted test first, then the broader feature validation command listed in `tasks.md`. A skipped or ignored test does not satisfy TDD unless the reason is documented in the task.
- **Traceability**: Each behavior-changing implementation task MUST be immediately preceded by a `[TDD-RED]` test task and an expected-failure run task, and followed by a `[TDD-GREEN]` pass-confirmation task.
- **Exact test files**: Use the concrete test file paths named by this feature `tasks.md` `[TDD-RED]` tasks; add new unit-test files there before production code when a behavior lacks coverage.

## Constitution Check

- **Mitigate/replay/prove closure**: Pass; core purpose.
- **Project boundary**: ARES owns replay/evidence/reporting; ENDI owns target behavior mitigation.
- **Evidence/evaluation**: Uses evaluator decisions.
- **Report/demo readiness**: Adds replay status to report.
- **Rust stack compliance**: Pass.

## Project Structure

```text
ares/src/replay/mod.rs
ares/src/replay/comparison.rs
ares/tests/mitigation_replay.rs
```

## Complexity Tracking

No constitution violations.
