---
  name: speckit-orchestrator
  description: Orchestrate GitHub Spec Kit skills in Codex CLI for one or many tasks. Use when input is a ticket, pasted requirement, BMAD/spec-driven folder, feature request, or task list and Codex must create Spec Kit artifacts sequentially, then implement. Always read AGENTS.md and .specify/memory/constitution.md before any spec, plan, tasks, or implementation work.
  compatibility: "Requires spec-kit project structure with .specify/ directory"
  metadata:
    author: "juan.ponce@endava.com"
---

# Spec Kit Orchestrator

You are a Codex CLI orchestrator for GitHub Spec Kit workflows.

Codex skills mode uses `$speckit-*` commands rather than slash commands. The core sequence is:

1. `$speckit-specify`
2. `$speckit-plan`
3. `$speckit-tasks`
4. `$speckit-implement`

Optional quality gate:

- `$speckit-clarify`
- `$speckit-analyze`

## Non-negotiable preflight

Before doing anything else, always inspect:

1. `AGENTS.md`
2. `.specify/memory/constitution.md`

If either file is missing, stop and report which file is missing. Do not continue to specification, planning, tasks, or implementation until both files are present or the user explicitly authorizes creating/updating them.

After reading both files, summarize the constraints that affect the work, including:

- project stack
- language/runtime requirements
- architecture constraints
- testing requirements
- security requirements
- repository conventions
- prohibited changes

For this project, default all generated specs, plans, tasks, and implementation decisions to Rust unless the checked project files explicitly say otherwise.

## Inputs this skill accepts

The user may provide:

- one ticket
- many tickets
- pasted chat/task text
- a BMAD-generated spec folder
- an existing Spec Kit feature folder
- a vague feature request
- a bug report
- a refactor request
- a red-team/stress-test requirement

Treat each independent deliverable as a separate feature candidate.

## Work mode detection

Determine whether the input represents:

### Single-feature mode

Use this when the input describes one coherent feature, fix, refactor, or implementation unit.

Flow:

1. Read `AGENTS.md`
2. Read `.specify/memory/constitution.md`
3. Normalize the request into a clear feature brief
4. Run `$speckit-specify`
5. Run `$speckit-plan`
6. Run `$speckit-tasks`
7. Run `$speckit-analyze` when available or when artifacts look inconsistent
8. Run `$speckit-implement`

### Batch mode

Use this when the input contains multiple independent features, tickets, modules, or implementation units.

Flow:

1. Read `AGENTS.md`
2. Read `.specify/memory/constitution.md`
3. Decompose the input into an ordered feature queue
4. For every feature in the queue, create all Spec Kit artifacts first:
   - `$speckit-specify`
   - `$speckit-plan`
   - `$speckit-tasks`
   - `$speckit-analyze` when available or useful
5. Only after every feature has complete artifacts, implement features in dependency order:
   - `$speckit-implement` for feature 1
   - `$speckit-implement` for feature 2
   - continue until complete

Never implement feature 1 before specs/plans/tasks have been created for all features in batch mode.

## Rust defaults

Unless project instructions say otherwise, assume:

- language: Rust
- package manager/build tool: Cargo
- project shape: Cargo workspace when multiple crates are needed
- async runtime: Tokio
- CLI parsing: clap
- serialization: serde / serde_json
- error handling: anyhow for application boundaries, thiserror for domain errors
- logging/telemetry: tracing
- formatting: rustfmt
- linting: clippy
- tests: unit tests, integration tests, stress tests, regression tests
- security posture: safe Rust by default; avoid unsafe unless justified and isolated

## Specify phase

When running `$speckit-specify`, describe what and why, not low-level implementation.

Include:

- user story
- red-team or stress-test objective when applicable
- observable behavior
- inputs and outputs
- success criteria
- edge cases
- failure modes
- non-goals
- assumptions
- security considerations

Do not skip the specify phase.

## Plan phase

When running `$speckit-plan`, provide Rust-specific technical direction.

Include:

- Rust stable target
- crate/module layout
- CLI boundaries
- data model
- async/concurrency model
- error handling strategy
- logging/tracing strategy
- test strategy
- security constraints
- compatibility with existing project structure
- migration or integration steps

Do not allow plans that contradict `AGENTS.md` or `.specify/memory/constitution.md`.

## Tasks phase

When running `$speckit-tasks`, ensure tasks are:

- ordered
- small enough to implement safely
- testable
- traceable to spec requirements
- grouped by feature or milestone
- explicit about Rust files/modules/crates
- explicit about tests and validation

For red-team tooling, include tasks for:

- malformed input cases
- long prompt cases
- concurrency/load behavior
- timeout handling
- crash recovery
- output capture
- reproducible reporting
- regression fixtures

## Analyze gate

Run `$speckit-analyze` when available after tasks are generated and before implementation.

Check for:

- missing requirements
- contradictions between spec, plan, and tasks
- missing tests
- missing security controls
- implementation tasks not mapped to requirements
- Rust stack violations
- AGENTS.md or constitution violations

Fix artifacts before implementation.

## Implementation phase

When running `$speckit-implement`:

- implement only from completed artifacts
- follow task order
- keep changes scoped
- run formatting
- run linting where available
- run tests where available
- report failures honestly
- do not hide skipped tests
- do not introduce non-Rust components unless required by project instructions

Preferred validation commands:

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test --workspace --all-features