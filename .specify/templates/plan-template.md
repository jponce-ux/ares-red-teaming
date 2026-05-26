# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]

**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Rust [stable toolchain + edition, e.g., Rust 1.xx / Edition 2024 or NEEDS CLARIFICATION]

**Primary Dependencies**: [Cargo crates, e.g., tokio, clap, tracing, serde, anyhow, thiserror or NEEDS CLARIFICATION]

**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]

**Testing**: cargo test, integration tests, stress/load tests, async/concurrency tests, clippy, rustfmt

**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]

**Project Type**: Rust Cargo workspace / CLI red teaming platform

**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]

**Constraints**: local-first execution, bounded concurrency, safe Rust, no tracked secrets, deterministic fixtures where possible

**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Defended target**: Plan identifies the chatbot target, system prompt scope,
  guardrails, and at least three verifiable behavior rules.
- **Attack coverage**: Plan lists manual and automated attack categories,
  including prompt injection, jailbreak/role manipulation, and system prompt
  extraction for MVP scope.
- **Reproducible fixtures**: Plan defines the attack input format, where attack
  prompts/templates live, and how variants are replayed.
- **Evidence and evaluation**: Plan specifies LLM-as-judge and/or heuristic
  evaluation, retained evidence, severity definitions, and review path for
  ambiguous results.
- **Mitigation replay**: Plan identifies how at least one mitigation will be
  applied and how the same attack set will be re-run to verify closure.
- **Local-first safety**: Plan keeps execution local except for configured model
  providers, keeps credentials out of tracked files, and safely constrains
  malicious-code or exfiltration scenarios.
- **Report and demo readiness**: Plan names Markdown or HTML report output and
  how show-and-tell will demonstrate target, attack, report, mitigation replay,
  and learning outcomes.
- **Rust stack compliance**: Plan uses Rust as the default language, identifies
  affected crates/modules, declares Rust edition/toolchain policy, and uses
  Cargo for dependency and workspace management.
- **Async and concurrency safety**: Plan uses Tokio for async execution,
  defines bounded concurrency, cancellation, retry, timeout, and load/stress
  behavior for concurrent red teaming workflows.
- **Rust quality gates**: Plan includes `cargo fmt --all --check`,
  `cargo clippy --workspace --all-targets --all-features`, and
  `cargo test --workspace`, plus scoped stress or async tests when relevant.
- **Error handling and observability**: Plan uses `Result`, `thiserror` for
  domain/library errors, `anyhow` at application boundaries, and `tracing` for
  structured execution evidence.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Rust Cargo workspace CLI + target chatbot (DEFAULT)
Cargo.toml
Cargo.lock
crates/
├── redteam-cli/
├── target-adapter/
├── attack-fixtures/
├── evaluator/
├── report/
├── provider-client/
└── domain/

attacks/
└── [category].jsonl

reports/
└── [generated report files]

tests/
├── integration/
├── stress/
├── async/
└── fixtures/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
