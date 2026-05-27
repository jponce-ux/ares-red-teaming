<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan:
.specify/specs/002-ollama-local-provider/plan.md
<!-- SPECKIT END -->

# Agent Instructions

## Official Stack

Rust is the official implementation language for ARES, the repository-root red
teaming project. AI agents MUST default to Rust for ARES code, specs,
examples, tests, and task plans unless the user explicitly requests a bounded
non-Rust artifact such as Markdown documentation, JSONL fixtures, or generated
reports.

Use Cargo workspace conventions by default. Prefer a modular crate architecture
with clear boundaries for CLI entrypoints, target adapters, attack fixtures,
evaluators, provider clients, report generation, shared domain types, and
stress/load tooling.

## Project Boundaries

The repository root is the ARES project root. ARES is the main project and the
main topic of this repository.

The `endi/` directory is a separate auxiliary Python CLI assistant project
that shares this repository root. ENDI is not the ARES runtime. When the user
asks for ENDI implementation work, keep all implementation files, tests, docs,
package metadata, local virtual environments, caches, and generated artifacts
inside `endi/`.

Spec Kit artifacts remain centralized under root `.specify/specs/`, including
specs for ENDI-targeted work. In specs, plans, and tasks, state the project
scope explicitly: ARES, ENDI, or cross-project integration. If scope is not
explicit and the paths do not point under `endi/`, assume ARES and use Rust.

For ENDI-scoped work, use the Python conventions declared by `endi/pyproject.toml`
and local commands run from `endi/`, such as:

- `UV_CACHE_DIR=.uv-cache UV_PYTHON_INSTALL_DIR=.uv-python uv pip install -e '.[dev]' --python .venv/bin/python`
- `.venv/bin/python -m pytest -q`
- `.venv/bin/ruff check src tests`
- `.venv/bin/mypy src`

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

All generated specs, plans, tasks, and implementation work MUST follow
test-driven development. For every new behavior, bug fix, refactor with
behavioral impact, or mitigation, agents MUST create or update the failing unit
test first, run the targeted test to record the expected failure, implement the
smallest production change needed to pass, rerun the targeted test, and only
then refactor while keeping tests green.

Task plans MUST make this red-green-refactor sequence explicit. A
behavior-changing implementation task is not ready unless it is preceded by a
test task that names the test file/module and targeted command. Skipped,
ignored, or unrun tests do not satisfy TDD unless the task documents the
reason and the remaining risk.

Generated ARES plans and implementation tasks MUST include Cargo workflows:

- `cargo fmt --all --check`
- `cargo clippy --workspace --all-targets --all-features`
- `cargo test --workspace`

ARES features that touch concurrency, load, provider resilience, attack
execution, or evaluator behavior MUST include relevant unit tests, integration
tests, stress/load tests, and async/concurrency tests. ENDI-scoped plans and
tasks MUST use ENDI's Python gates from `endi/pyproject.toml` instead.

Prefer deterministic unit tests before integration, stress, load, or
end-to-end tests. For cross-project ARES/ENDI work, add unit tests on each
side of the contract where behavior changes, plus contract/integration tests
for serialized subprocess input/output when applicable.

## Security Defaults

Use safe Rust. `unsafe` is prohibited unless a plan documents the need,
invariants, tests, and review path. Do not hardcode real secrets, real
customer data, or operationally harmful payloads. Prompt injection, jailbreak,
malicious-code, and exfiltration scenarios MUST be simulated or safely
constrained for lab use.

Prefer secure-by-default CLI behavior: explicit config, no tracked credentials,
bounded resource usage, deterministic fixtures when possible, auditable report
output, and clear failure modes.
