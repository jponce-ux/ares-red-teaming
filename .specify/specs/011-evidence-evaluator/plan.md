# Implementation Plan: Evidence Capture and Rule Violation Evaluation

**Branch**: `[011-evidence-evaluator]` | **Date**: 2026-05-27 | **Spec**: [spec.md](spec.md)

## Summary

Implement isolated evidence capture and deterministic evaluator logic that assigns auditable decisions, severities, rationales, and heuristic matches for attack results.

## Technical Context

**Project Scope**: ARES root Rust project
**Language/Version**: Rust stable
**Primary Dependencies**: `serde`, `thiserror`, `regex` or string matching, `tracing`
**Storage**: Structured in-memory evidence records for report output
**Testing**: Unit tests for each heuristic family and decision state
**Target Platform**: Local CLI
**Constraints**: No uncontrolled sensitive evidence in logs; deterministic evaluator first.

## Constitution Check

- **Evidence/evaluation**: Pass; core purpose.
- **Attack coverage**: Heuristics cover MVP rule classes.
- **Mitigation replay**: Decisions support before/after comparison.
- **Rust stack compliance**: Pass.
- **Rust quality gates**: Included.

## Project Structure

```text
ares/src/evaluator/mod.rs
ares/src/evaluator/heuristics.rs
ares/src/evaluator/evidence.rs
ares/tests/evaluator.rs
```

## Complexity Tracking

No constitution violations.
