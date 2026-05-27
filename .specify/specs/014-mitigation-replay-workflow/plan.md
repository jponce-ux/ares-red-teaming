# Implementation Plan: Mitigation Replay Workflow

**Branch**: `[014-mitigation-replay-workflow]` | **Date**: 2026-05-27 | **Spec**: [spec.md](spec.md)

## Summary

Implement ARES replay comparison logic that can load baseline results, run or load post-mitigation results, classify mitigation outcomes by stable attack ID, and feed replay status into reports.

## Technical Context

**Project Scope**: Cross-project integration
**Language/Version**: Rust stable
**Primary Dependencies**: `serde`, existing runner/evaluator/report modules, `thiserror`
**Storage**: Structured result files and replay comparison output
**Testing**: Unit tests for comparison and report integration tests
**Target Platform**: Local CLI
**Constraints**: No ENDI source changes; stable attack IDs required; safely handle missing/malformed result files.

## Constitution Check

- **Mitigate/replay/prove closure**: Pass; core purpose.
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
