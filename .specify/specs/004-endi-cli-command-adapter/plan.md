# Implementation Plan: ENDI CLI Command Adapter

**Branch**: `[004-endi-cli-command-adapter]` | **Date**: 2026-05-27 | **Spec**: [spec.md](spec.md)

## Summary

Implement an ARES-side Rust adapter that invokes ENDI using structured process arguments, captures outputs and metadata, enforces timeouts, and returns typed results/errors without changing ENDI.

## Technical Context

**Project Scope**: Cross-project integration
**Language/Version**: Rust stable, edition 2024 unless existing scaffold uses 2021
**Primary Dependencies**: `tokio`, `thiserror`, `tracing`, `serde` if result serialization is needed
**Storage**: N/A
**Testing**: Cargo fmt, clippy, unit/integration tests with controlled commands
**Target Platform**: Local CLI
**Project Type**: ARES Rust CLI module
**Performance Goals**: Adapter respects configured timeout for every process call.
**Constraints**: Do not modify ENDI; no shell interpolation; redact prompt in logs unless retained as evidence.
**Scale/Scope**: Single command execution API for later runner use.

## Constitution Check

- **Defended target**: Adapter enables ENDI target interaction.
- **Attack coverage**: Deferred to category tickets.
- **Evidence and evaluation**: Captures output metadata for later evidence.
- **Mitigation replay**: Deferred.
- **Local-first safety**: Pass; local process execution.
- **Rust stack compliance**: Pass.
- **Async/concurrency safety**: Uses Tokio process and timeout.
- **Rust quality gates**: Included.
- **Project boundary**: Pass; ARES calls ENDI, ENDI source unchanged.

## Project Structure

```text
ares/src/targets/endi.rs
ares/src/targets/mod.rs
ares/tests/endi_adapter.rs
```

**Structure Decision**: Place ENDI process integration under ARES target adapter modules.

## Complexity Tracking

No constitution violations.
