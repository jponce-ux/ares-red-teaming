# Implementation Plan: ARES Rust CLI Scaffold and Workspace Baseline

**Branch**: `[003-ares-rust-cli-scaffold]` | **Date**: 2026-05-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `.specify/specs/003-ares-rust-cli-scaffold/spec.md`

## Summary

Create the initial ARES Rust CLI scaffold using Cargo, `clap`, `anyhow`, and `tracing`, with module placeholders for targets, attacks, runner, evaluator, and reporting. Keep ENDI untouched and avoid nested Git repositories.

## Technical Context

**Project Scope**: ARES root Rust project
**Language/Version**: Rust stable, edition 2024 unless the local toolchain requires edition 2021 during bootstrap
**Primary Dependencies**: `clap`, `anyhow`, `tracing`, `tracing-subscriber`
**Storage**: N/A
**Testing**: `cargo fmt --all --check`; `cargo clippy --workspace --all-targets --all-features`; `cargo test --workspace`
**Target Platform**: Local CLI on developer workstation
**Project Type**: Rust Cargo CLI workspace/package
**Performance Goals**: CLI startup and help must complete quickly enough for interactive use.
**Constraints**: No ENDI source changes; no nested `.git/`; safe Rust; no secrets.
**Scale/Scope**: Bootstrap command structure only.

## Constitution Check

- **Defended target**: Deferred to ENDI adapter/target tickets; scaffold provides module space.
- **Attack coverage**: Deferred; scaffold only.
- **Evidence and evaluation**: Deferred; scaffold only.
- **Mitigation replay**: Deferred; scaffold only.
- **Local-first safety**: Pass; local CLI only.
- **Rust stack compliance**: Pass; Rust/Cargo first.
- **Async/concurrency safety**: No async behavior yet.
- **Rust quality gates**: Included.
- **Project boundary**: Pass; ARES only, ENDI untouched.

## Project Structure

```text
ares/
├── Cargo.toml
└── src/
    ├── main.rs
    ├── cli.rs
    ├── config.rs
    ├── targets/
    ├── attacks/
    ├── runner/
    ├── evaluator/
    └── reporting/
```

**Structure Decision**: Use a Rust CLI package under `ares/` while keeping the top-level repository as the only Git repository. Future tickets may promote this to a root Cargo workspace if multiple crates are introduced.

## Complexity Tracking

No constitution violations.
