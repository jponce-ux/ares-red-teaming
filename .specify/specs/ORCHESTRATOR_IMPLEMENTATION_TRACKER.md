# Orchestrator Implementation Tracker

**Purpose**: Repo-level follow-up checklist for implementing all current Spec Kit feature folders under `.specify/specs/`.

**Audience**: `speckit-orchestrator` and human reviewers coordinating the implementation batch.

**Created**: 2026-05-27

## Usage

When invoking the orchestrator for batch implementation, reference this file and require it to:

1. Read `AGENTS.md`, `.specify/memory/constitution.md`, and `.specify/memory/ba-pm-decisions.md`.
2. Treat `002-ollama-local-provider` as completed/historical unless a new Ollama change is explicitly requested.
3. Implement only active pending specs.
4. Follow each feature's `tasks.md` order.
5. Use the TDD loop required by each active feature:
   - Red: add/update failing test.
   - Red: run targeted test and record expected failure.
   - Green: implement the smallest production change.
   - Green: run targeted test and record pass.
   - Refactor only after green.
   - Validate broader gates.
6. Mark completed tasks as `[x]` in the relevant `tasks.md`.
7. Update the progress columns in this tracker after each feature is completed.

## Global Gates

- [ ] CHK001 Are ARES implementation tasks kept under `ares/` and root Cargo workspace files unless the task explicitly targets documentation or Spec Kit artifacts? [Boundary]
- [ ] CHK002 Are ENDI implementation tasks kept under `endi/` with ENDI Python validation commands? [Boundary]
- [ ] CHK003 Are all behavior-changing tasks implemented through failing tests first, targeted red-phase command, minimal implementation, and green-phase confirmation? [TDD]
- [ ] CHK004 Are real secrets, real customer data, and operationally harmful payloads excluded from fixtures, tests, logs, and reports? [Security]
- [ ] CHK005 Are all ARES code changes validated with `cargo fmt --all --check`, `cargo clippy --workspace --all-targets --all-features`, and `cargo test --workspace` unless a narrower command is documented? [Quality Gate]
- [ ] CHK006 Are all ENDI code changes validated from `endi/` with `.venv/bin/python -m pytest -q`, `.venv/bin/ruff check src tests`, and `.venv/bin/mypy src` unless a narrower command is documented? [Quality Gate]
- [ ] CHK007 Are manual attack rows and reflection checkpoints treated as incomplete while `TBD` remains? [Evidence]
- [ ] CHK008 Is the ENDI target policy mitigation from `018` implemented before ARES mitigation replay in `014` is considered complete? [Dependency]

## Implementation Queue

Recommended order balances dependencies and project boundaries. `002` is intentionally excluded from active implementation because it is completed/historical.

| Order | Feature | Scope | Status | Tasks | TDD Red | TDD Green | Depends On | Progress | Notes |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| 01 | `001-endi-runtime-completion` | ENDI Python | Active | 32 | 14 | 20 | None | Not started | Finish or reconcile ENDI runtime foundation before target policy work if missing provider seams affect `018`. |
| 02 | `018-endi-target-policy-mitigation` | ENDI Python | Draft | 21 | 9 | 11 | `001` provider/CLI seams | Not started | Concrete MVP mitigation for C1. Required before `014` replay closure. |
| 03 | `003-ares-rust-cli-scaffold` | ARES Rust | Draft | 13 | 5 | 5 | None | Not started | Establish root Cargo workspace and ARES binary crate. |
| 04 | `004-endi-cli-command-adapter` | ARES Rust + ENDI CLI contract | Draft | 16 | 5 | 9 | `003`, ENDI CLI available | Not started | ARES must subprocess ENDI; no Python imports. |
| 05 | `006-ares-runtime-configuration` | ARES Rust | Draft | 13 | 5 | 9 | `003`, target decisions | Not started | TOML config only for MVP. |
| 06 | `005-attack-domain-fixture-schema` | ARES Rust | Draft | 14 | 6 | 7 | `003`, `017` | Not started | JSONL attack fixtures and TOML target fixture. |
| 07 | `017-endi-target-profile-decisions` | Decision artifacts | Draft | 10 | 3 | 3 | BA/PM memory | Not started | Mostly documentation; use `[DOCS]` tasks as artifact quality work. |
| 08 | `007-prompt-injection-attacks` | ARES Rust fixtures | Draft | 10 | 5 | 5 | `005`, `017` | Not started | MVP attack category. |
| 09 | `008-jailbreak-roleplay-attacks` | ARES Rust fixtures | Draft | 10 | 5 | 5 | `005`, `017` | Not started | MVP attack category. |
| 10 | `009-system-prompt-extraction-attacks` | ARES Rust fixtures | Draft | 10 | 5 | 5 | `005`, `017` | Not started | MVP attack category. |
| 11 | `010-attack-runner-concurrency` | ARES Rust | Draft | 16 | 7 | 10 | `004`, `005`, `006`, attack fixtures | Not started | Sequential first, bounded concurrency next. |
| 12 | `011-evidence-evaluator` | ARES Rust | Draft | 15 | 5 | 10 | `005`, `010`, `017` | Not started | Must follow `heuristic-matrix.md`. |
| 13 | `012-markdown-vulnerability-report` | ARES Rust | Draft | 14 | 5 | 9 | `010`, `011`, `013`, `014` types as available | Not started | Include manual/reflection artifact status. |
| 14 | `013-manual-attack-documentation` | Evidence docs | Draft | 9 | 3 | 3 | ENDI runnable target, `017` | Not started | Requires real ENDI responses before MVP evidence complete. |
| 15 | `014-mitigation-replay-workflow` | ARES Rust + ENDI mitigation dependency | Draft | 14 | 5 | 9 | `010`, `011`, `012`, `018` | Not started | Do after baseline and `018` mitigation. |
| 16 | `015-endi-stress-test-mode` | ARES Rust | Draft | 12 | 5 | 8 | `004`, `006`, `010` | Not started | Bounded stress/load behavior. |
| 17 | `016-cli-observability-audit` | ARES Rust | Draft | 15 | 6 | 9 | Core runner/evaluator/report modules | Not started | Can introduce run ID early, integrate fully after core modules. |
| Historical | `002-ollama-local-provider` | ENDI Python | Completed | 22 checked | 0 | 0 | None | Complete | Do not reopen unless explicitly requested; create a new TDD spec for future Ollama changes. |

## Phase Checklists

### Phase A - ENDI Target Readiness

- [ ] CHK009 Are ENDI runtime prerequisites from `001` either implemented or confirmed already available for `018`? [Dependency]
- [ ] CHK010 Is `018` implemented with target policy loading, `--system-prompt-file`, provider message ordering, structured errors, and `endi/config/target_policy.md`? [Completeness]
- [ ] CHK011 Are ENDI validation gates green after `001` and `018` work? [Quality Gate]

### Phase B - ARES Foundation

- [ ] CHK012 Is the root Cargo workspace created with `members = ["ares"]` and `resolver = "2"`? [Completeness]
- [ ] CHK013 Is `endi/` excluded from the Cargo workspace? [Boundary]
- [ ] CHK014 Does ARES expose a runnable CLI help path before feature modules depend on it? [Dependency]
- [ ] CHK015 Are Rust quality gates green after the scaffold? [Quality Gate]

### Phase C - ARES-to-ENDI Contract

- [ ] CHK016 Are `EndiClient::version`, `chat`, `submit`, and `validate_environment` implemented through subprocess execution only? [Contract]
- [ ] CHK017 Does the adapter capture command, stdout, stderr, exit code, started time, duration, timeout, parsed ENDI JSON, and errors? [Completeness]
- [ ] CHK018 Are prompt contents redacted from tracing by default while controlled evidence can retain them? [Security]

### Phase D - Attack Definitions and Execution

- [ ] CHK019 Are target rules R1-R5 represented as strong domain types? [Completeness]
- [ ] CHK020 Are JSONL fixtures present for prompt injection, jailbreak/role-play, and system prompt extraction with 3-5 variants each? [Coverage]
- [ ] CHK021 Is `ares/fixtures/targets/endi_support.toml` present and aligned to the ENDI target profile? [Consistency]
- [ ] CHK022 Does the runner execute attacks sequentially before bounded concurrency is enabled? [Dependency]
- [ ] CHK023 Are timeouts, target errors, and harness errors represented as statuses rather than severities? [Consistency]

### Phase E - Evaluation and Reporting

- [ ] CHK024 Is evaluator behavior implemented from `011/heuristic-matrix.md` with conservative success classification? [Traceability]
- [ ] CHK025 Are severity values assigned only to `success` or `partial` results? [Consistency]
- [ ] CHK026 Does the Markdown report include run status summary, severity counts, evidence excerpts, mitigation suggestions, manual/reflection artifact status, and limitations? [Completeness]

### Phase F - Manual Evidence and Mitigation Replay

- [ ] CHK027 Are five manual attacks recorded with real ENDI commands and raw responses across required categories? [Evidence]
- [ ] CHK028 Are Reflection 1 and Reflection 2 filled with real observations rather than placeholders? [Evidence]
- [ ] CHK029 Is baseline attack output preserved before applying ENDI mitigation? [Traceability]
- [ ] CHK030 Is post-mitigation replay compared by stable attack ID and classified as closed, reduced, unchanged, or regressed? [Measurability]

### Phase G - Stress and Observability

- [ ] CHK031 Does stress mode use bounded concurrency and capture latency/failure summaries? [Non-Functional]
- [ ] CHK032 Are run IDs propagated through CLI, runner, evaluator, report, and logs? [Traceability]
- [ ] CHK033 Are structured tracing events emitted without raw prompt/response leakage by default? [Security]

## Per-Feature Completion Template

Use this block when updating progress for each feature:

```text
Feature:
Started:
Completed:
Red-phase commands run:
Expected failures recorded:
Green-phase commands run:
Broader validations:
Tasks marked [x] in:
Notes / blockers:
```

## Known Blockers to Watch

- `013` is incomplete until all `TBD` values are replaced by real evidence.
- `014` must wait for `018` and baseline attack evidence.
- `012` can generate report types early, but final report completeness depends on evaluator, manual evidence, and replay outputs.
- `016` can introduce run ID types early, but full observability depends on runner/evaluator/report integration points.
