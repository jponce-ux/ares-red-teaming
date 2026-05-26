<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan.
<!-- SPECKIT END -->

# Agent Instructions

## Official Stack

Rust is the official implementation language for this repository. AI agents
MUST default to Rust for generated code, specs, examples, tests, and task
plans unless the user explicitly requests a bounded non-Rust artifact such as
Markdown documentation, JSONL fixtures, or generated reports.

Use Cargo workspace conventions by default. Prefer a modular crate architecture
with clear boundaries for CLI entrypoints, target adapters, attack fixtures,
evaluators, provider clients, report generation, shared domain types, and
stress/load tooling.

## Rust Conventions

Generated Rust MUST follow idiomatic ownership, borrowing, and strong typing.
Represent attack cases, target rules, severities, evaluator decisions,
mitigation replay states, provider responses, and run identifiers as explicit
domain types instead of loosely typed strings or maps.

Use Tokio for async-first implementations. Concurrent attack execution,
provider calls, streaming, retries, timeouts, cancellation, and stress tests
MUST use bounded concurrency and predictable failure handling.

Use `Result` for fallible operations. Library crates SHOULD expose typed
errors with `thiserror`; CLI/application boundaries MAY use `anyhow` with
context. Avoid `unwrap`, `expect`, and panics in production code unless the
invariant is local, documented, and unrecoverable.

Use `tracing` for logging and observability. Red-team runs, attack execution,
provider calls, evaluator decisions, report generation, retries, timeouts, and
concurrency limits MUST emit structured spans or events. Redact secrets and
sensitive data unless the content is intentionally retained as controlled test
evidence.

## Quality Gates

Generated plans and implementation tasks MUST include Cargo workflows:

- `cargo fmt --all --check`
- `cargo clippy --workspace --all-targets --all-features`
- `cargo test --workspace`

Features that touch concurrency, load, provider resilience, attack execution,
or evaluator behavior MUST include relevant unit tests, integration tests,
stress/load tests, and async/concurrency tests.

## Security Defaults

Use safe Rust. `unsafe` is prohibited unless a plan documents the need,
invariants, tests, and review path. Do not hardcode real secrets, real
customer data, or operationally harmful payloads. Prompt injection, jailbreak,
malicious-code, and exfiltration scenarios MUST be simulated or safely
constrained for lab use.

Prefer secure-by-default CLI behavior: explicit config, no tracked credentials,
bounded resource usage, deterministic fixtures when possible, auditable report
output, and clear failure modes.
