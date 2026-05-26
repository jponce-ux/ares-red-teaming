<!--
Sync Impact Report
Version change: 1.1.0 -> 1.1.1
Modified principles:
- I. Build a Defended Target Before Attacking -> unchanged
- II. Categorized, Reproducible Attack Coverage -> unchanged
- III. Evidence-Based Vulnerability Evaluation -> unchanged
- IV. Mitigate, Replay, and Prove Closure -> unchanged
- V. Rust-First, Local, Auditable CLI Workflow -> V. ARES Rust-First, Local, Auditable CLI Workflow
Added sections:
- Project Boundaries and Auxiliary ENDI Project
Removed sections:
- None
Templates requiring updates:
- ✅ updated .specify/templates/plan-template.md
- ✅ updated .specify/templates/spec-template.md
- ✅ updated .specify/templates/tasks-template.md
- ✅ reviewed .specify/templates/checklist-template.md
- ✅ reviewed .specify/templates/commands/*.md (directory absent)
- ✅ updated AGENTS.md
Follow-up TODOs:
- None
-->
# RedTeam AI Security Lab Constitution

## Core Principles

### I. Build a Defended Target Before Attacking
Every implementation MUST include a runnable chatbot target before automated
red teaming work is considered complete. The target MUST have a system prompt,
a support-oriented role or explicitly documented alternate domain, basic
guardrails where supported by the chosen model, and at least three verifiable
behavior rules. At minimum, the target MUST include rules for refusing system
prompt disclosure, refusing malicious code generation, and staying within its
declared support domain unless the feature specification justifies a different
target. Rationale: teams cannot evaluate AI red teaming techniques without
first understanding how the defended AI system is constructed.

### II. Categorized, Reproducible Attack Coverage
Manual and automated attacks MUST be categorized, repeatable, and preserved as
project artifacts. The MVP MUST document at least five manual attacks across
distinct categories and automate at least three categories with three to five
variants each. Required MVP categories are prompt injection, jailbreak or
role-play manipulation, and system prompt extraction. Attack definitions MUST
record category, prompt or template, expected policy violation, and target
rule under test. Rationale: red teaming without reproducible coverage becomes
anecdotal and cannot support regression checks.

### III. Evidence-Based Vulnerability Evaluation
Every attack execution MUST produce evidence that supports a success or
failure decision. The redteam CLI MUST evaluate whether the chatbot violated
its rules using a documented method, such as LLM-as-judge, deterministic
heuristics, or both. Each result MUST keep the attack prompt, chatbot response,
evaluation decision, severity, and evaluator rationale or matched heuristic.
Critical, high, medium, and low severity levels MUST be defined in project
documentation and applied consistently. Rationale: automatic evaluation is
useful only when humans can inspect why a result was classified.

### IV. Mitigate, Replay, and Prove Closure
At least one discovered vulnerability MUST receive a concrete mitigation before
the MVP is complete. The same relevant attack set MUST be re-run after the
mitigation, and the report MUST show whether the vulnerability was closed,
partially reduced, or still open. Mitigations MAY include system prompt
changes, additional guardrails, stricter routing, output filtering, or
evaluator changes, but they MUST be tied to observed attack evidence.
Rationale: the lab outcome is learning which defenses work, not only listing
failures.

### V. ARES Rust-First, Local, Auditable CLI Workflow
The official implementation language for the ARES red teaming project is Rust.
Production code, examples, generated specs, and automation defaults for ARES
MUST assume Rust unless a feature specification documents a bounded non-Rust
artifact such as generated reports or test data. The red teaming workflow MUST
run locally without cloud infrastructure beyond the selected model provider.
The CLI MUST support machine-readable attack input and produce a Markdown or
HTML report with an executive summary, vulnerabilities by category, severities,
successful prompts, and mitigation suggestions. Configuration MUST keep
provider credentials outside tracked source files. Rationale: Rust gives ARES
a memory-safe, strongly typed foundation for AI chat stress testing,
concurrent red teaming, failure analysis, and repeatable local tooling.

## Project Boundaries and Auxiliary ENDI Project

The repository root is the ARES project root. ARES is the main project and the
main topic of this repository: a Rust-based red teaming and AI chat stress
testing platform.

The `endi/` directory is a separate auxiliary Python CLI assistant project that
shares this repository root for convenience. ENDI is not the ARES runtime and
is not governed by the Rust implementation requirement except where a
cross-project integration specification explicitly says so. ENDI MAY continue
to use Python, its own `pyproject.toml`, and its own local virtual environment
inside `endi/`.

Any implementation work for ENDI MUST stay inside `endi/`, including source,
tests, documentation, local Python environment files, package metadata, and
BMAD-derived ENDI artifacts. ENDI work MUST NOT introduce Python project files,
virtual environments, package caches, or generated Python artifacts at the
repository root.

Spec Kit artifacts remain centralized at the repository root under
`.specify/specs/`, even when a specification targets ENDI. A specification
that targets ENDI MUST state that scope explicitly and MUST use implementation
paths under `endi/`. A specification that does not explicitly target ENDI
defaults to ARES and MUST follow the Rust-first ARES rules.

Cross-project work MUST name both sides and keep ownership boundaries clear.
ARES MAY call, wrap, or test ENDI only through a documented integration
contract. ENDI MAY support ARES workflows only through files and interfaces
defined in that integration contract.

## Official Rust Technology Stack

ARES first-party executable code MUST be written in Rust using Cargo. The ARES
root MUST use a Cargo workspace when there is more than one crate, with crates
organized around clear red teaming responsibilities such as CLI entrypoints,
target adapters, attack fixtures, evaluators, report generation, provider
clients, load/stress execution, and shared domain types. This Rust stack rule
does not apply to the separate ENDI Python project inside `endi/`.

Rust edition policy MUST be explicit in each `Cargo.toml`. New crates MUST use
the current stable Rust edition available to the project at creation time, and
edition upgrades MUST be handled as planned maintenance with `cargo fix
--edition`, tests, and review. Toolchain changes MUST be documented in the
implementation plan and SHOULD be pinned with `rust-toolchain.toml` when team
reproducibility requires it.

Dependency management MUST use Cargo and checked-in `Cargo.lock` for runnable
applications and CLI binaries. Dependencies MUST be justified by feature need,
kept narrowly scoped by crate, and reviewed for maintenance status, license,
security posture, and transitive risk. Feature flags MUST be explicit when they
change attack execution, provider access, concurrency behavior, or report
output.

Async work MUST use Tokio as the standard runtime. Red teaming code that
executes concurrent attacks, provider calls, streaming responses, timeout
handling, retries, or load tests MUST use structured async patterns with
bounded concurrency, cancellation, backoff, and timeouts. Blocking operations
inside async paths MUST be isolated with Tokio's blocking facilities or moved
outside the async path.

Error handling MUST use `Result` and typed errors. Library crates MUST expose
domain-specific errors using `thiserror` where callers need to match variants.
Application and CLI boundaries MAY use `anyhow` for contextual reporting.
Panics, `unwrap`, and `expect` MUST NOT appear in production paths unless the
invariant is local, documented, and unrecoverable; tests MAY use them when they
make assertions clearer.

Logging and observability MUST use `tracing`. CLI execution, attack runs,
provider calls, evaluator decisions, retries, concurrency limits, timeouts,
and report generation MUST emit structured spans or events that can be tied to
an attack run and correlation identifier. Secrets and sensitive prompt content
MUST be redacted from logs unless explicitly retained as controlled test
evidence.

Security-first Rust practices are mandatory. Implementations MUST prefer safe
Rust, ownership-driven design, strong domain types, input validation, explicit
serialization schemas, bounded resource usage, and secure defaults. `unsafe`
code is prohibited unless a feature plan documents why it is necessary, what
invariants protect it, and how it is tested. Real secrets, real customer data,
and operationally harmful payloads MUST NOT be embedded in tests, fixtures,
logs, or reports.

## Lab Scope and Constraints

This repository exists for Lab 16: RedTeam - Seguridad y Red Teaming de
Sistemas de IA. The primary product is a defended chatbot target plus a
redteam CLI that executes categorized attacks and reports vulnerabilities.

The MVP MUST include two learning phases. Phase one builds the target,
researches common AI attack vectors, runs manual attacks, documents results in
a table, categorizes vulnerabilities, assigns severity, and records a
reflection checkpoint about AI tool usage. Phase two designs the automated
attack suite, implements the redteam CLI, evaluates attack success, generates a
Markdown or HTML report, applies at least one mitigation, re-runs the attacks,
and records a second reflection checkpoint.

The project MUST treat the chatbot target as intentionally vulnerable enough
to learn from but MUST NOT include real secrets, real customer data, or
instructions that enable real-world harm. Malicious-code and exfiltration
scenarios MUST be simulated or safely constrained. Extension work MAY add
LLM-generated attack variants, indirect prompt injection, exfiltration
simulation, security dashboards, or CI/CD integration, provided the MVP
evidence and mitigation loop remain intact.

## Rust Development Workflow and Quality Gates

Feature specifications MUST identify the target rules under test, the attack
categories in scope, the evaluation method, the report format, and the
mitigation replay plan. They MUST also identify affected Rust crates, public
types, async boundaries, Cargo features, and CLI commands. Implementation
plans MUST pass a Constitution Check before coding by showing how the feature
preserves local execution, reproducible attacks, auditable evidence, safe
handling of credentials and test data, Rust memory safety, and bounded
concurrency.

Task plans MUST include explicit tasks for target behavior rules, manual attack
documentation, attack fixture creation, automated CLI execution, evaluator
implementation, reporting, mitigation, replay verification, and reflection
checkpoints. They MUST include Rust-specific tasks for crate/module structure,
Cargo dependency changes, typed error handling, async runtime integration,
`tracing` instrumentation, and CLI contract behavior. Tests or validation
scripts MUST cover attack parsing, target rule enforcement, evaluator
decisions, report generation, mitigation regression, unit behavior,
integration flows, stress/load behavior, and async/concurrency behavior where
applicable.

Every code change MUST pass `cargo fmt --all --check`, `cargo clippy
--workspace --all-targets --all-features`, and `cargo test --workspace` unless
the plan documents why a narrower command is valid. Features that touch
concurrent attack execution or provider resilience MUST add stress tests or
load-oriented validation with bounded runtime, deterministic fixtures where
possible, and documented limits. Public Rust APIs MUST be strongly typed and
organized so invalid attack states, severity states, and evaluator decisions
are hard to represent.

Show-and-tell readiness requires a runnable chatbot, at least one demonstrated
successful attack, the generated vulnerability report, evidence of one
mitigation replay, and a discussion of which defenses worked, which failed,
and what the team learned about LLM robustness.

## Governance

This constitution supersedes conflicting project practices, templates, and
ad-hoc implementation decisions. Amendments MUST update this file, include a
Sync Impact Report, and review dependent spec-kit templates for consistency.

Versioning follows semantic versioning. MAJOR changes remove or redefine core
principles or compatibility expectations. MINOR changes add principles,
required sections, or materially expand governance. PATCH changes clarify
language without changing obligations.

Every feature plan and review MUST verify compliance with the Core Principles.
Any intentional violation MUST be documented in the plan's Complexity Tracking
section with the reason, rejected simpler alternative, risk, and expected
follow-up. Outstanding constitution TODOs, if any, MUST be resolved before the
affected feature is considered complete.

**Version**: 1.1.1 | **Ratified**: 2026-05-26 | **Last Amended**: 2026-05-26
