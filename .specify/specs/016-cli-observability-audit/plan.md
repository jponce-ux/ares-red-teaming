# Implementation Plan: CLI Observability, Run IDs, and Audit Logging

**Branch**: `[016-cli-observability-audit]` | **Date**: 2026-05-27 | **Spec**: [spec.md](spec.md)

## Summary

Add typed run IDs, structured `tracing` events, configurable verbosity, default redaction, and report/run metadata propagation across ARES CLI workflows.

## Technical Context

**Project Scope**: ARES root Rust project
**Language/Version**: Rust stable
**Primary Dependencies**: `tracing`, `tracing-subscriber`, `uuid` or typed ID generation, `serde`
**Storage**: Structured logs to stderr/file depending on config
**Testing**: Unit/integration validation for run ID propagation and redaction
**Target Platform**: Local CLI
**Constraints**: Do not log raw prompts by default; machine-readable audit fields where practical.

## Constitution Check

- **Evidence/evaluation**: Auditability improved with run IDs.
- **Local-first safety**: Pass.
- **Logging/observability**: Pass; uses `tracing`.
- **Rust stack compliance**: Pass.
- **Rust quality gates**: Included.

## Project Structure

```text
ares/src/observability/mod.rs
ares/src/observability/redaction.rs
ares/tests/observability.rs
```

## Complexity Tracking

No constitution violations.
