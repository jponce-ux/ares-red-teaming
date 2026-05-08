# Epic Retrospective: epic-mvp-03

Date: 2026-03-23
Facilitator: Scrum Master workflow (`bmad-retrospective`)
Scope: `EPIC-MVP-03` (stories `mvp-03-1`, `mvp-03-2`, `mvp-03-3`, `mvp-03-4`)

## Epic Outcome Snapshot
- Stories completed: 4/4 (`done`)
- Current sprint status state before closeout update: `epic-mvp-03: in-progress` while all child stories are `done`
- Retrospective status before this artifact: `epic-mvp-03-retrospective: optional`
- Previous retrospective reference: `_bmad-output/implementation-artifacts/epic-mvp-02-retro-2026-03-19.md`

## Epic Goals vs Outcomes
### Goal 1: Deliver local durable execution history (`MVP-03.1`)
- **Target:** SQLite-backed durable timeline across `session`, `command`, `workflow`, `step`, `tool_call`, `runtime_error` with atomic writes and deterministic query reconstruction.
- **Outcome:** Achieved. Persistence baseline shipped with atomic stage-transition writes, deterministic timeline reconstruction by `execution_id`, and structured persistence failure mapping.

### Goal 2: Deliver traceable structured telemetry baseline (`MVP-03.2`)
- **Target:** Deterministic structured envelopes and baseline correlation hierarchy (`session -> command -> workflow -> step`) with structured error classification.
- **Outcome:** Achieved. Canonical telemetry envelope fields and baseline chain continuity are implemented with shared-boundary parity coverage.

### Goal 3: Extend conversational correlation chain (`MVP-03.4`)
- **Target:** Additive conversational correlation for `agent` and `tool_call` with strict parent-link integrity guarantees.
- **Outcome:** Achieved. Conversational path now emits deterministic additive correlation events and blocks invalid lineage via structured validation/runtime errors.

### Goal 4: Enforce bounded local retention (`MVP-03.3`)
- **Target:** Locked defaults (`30 days`, `2 GB`, `auto_prune=true`) with deterministic age-first then size-based prune behavior.
- **Outcome:** Achieved. Retention defaults and deterministic prune ordering are enforced with transactional safety and structured retention summaries.

## What Went Well
- The epic maintained strong deterministic behavior contracts across persistence, telemetry, and retention paths.
- Strict quality-gate discipline remained consistent through implementation and post-review hardening.
- Shared command/conversation boundaries retained parity while allowing additive conversational observability extension.
- Sensitive-by-default handling stayed explicit and test-backed across telemetry, persistence, and runtime error surfaces.
- Review cycles improved implementation quality, especially around retention size accounting and validation hardening.

## What Didn’t Go Well / Risks Encountered
- Epic closeout status drift persisted until retrospective closeout (`epic-mvp-03` remained `in-progress` despite all stories `done`).
- Several hardening fixes landed post-review instead of being prevented earlier by first-pass acceptance tests.
- Retention edge behavior required additional correction for SQLite active-size accounting to avoid over-pruning.
- Retention override validation required stricter input parsing to avoid ambiguous behavior.

## Quality-Gate Evidence Summary
- Gate model for MVP-03 implementation stories remained `Strict`.
- Standard gates used: `ruff check src tests`, `mypy src`, `pytest` (WSL project `.venv`).
- Story-level recorded evidence:
  - `MVP-03.1`: gates passed; `pytest` evidence `80 passed`.
  - `MVP-03.2`: gates passed; `pytest` evidence `83 passed`.
  - `MVP-03.4`: gates passed; `pytest` evidence `87 passed`.
  - `MVP-03.3`: gates passed; `pytest` evidence `98 passed`.
- Result: no open lint/type/test failures carried into epic closeout.

## Contract / Guardrail Compliance Summary
### Deterministic behavior
- Implemented and validated for envelope fields, correlation hierarchy continuity, parent-link failure classification, and retention prune ordering.

### Safety-by-default
- Runtime and retention paths remained fail-safe with structured error outcomes for invalid contracts and unsafe conditions.

### Command/conversation parity
- Shared externally observable boundaries remained schema-compatible with additive-only conversational extensions.

### Sensitive-by-default handling
- Raw free-form text remained excluded/sanitized by default in persistence rows, telemetry payloads, and runtime error envelopes.

## Key Lessons Learned
- Deterministic observability/persistence contracts are effective only when they are covered by boundary-focused regressions from the first implementation pass.
- Parent-link integrity checks and additive-only extension rules are critical to scale observability safely between command and conversational paths.
- Retention logic should treat active SQLite storage metrics explicitly; relying on allocated size can create non-deterministic prune pressure.
- Story-level engineering discipline was strong; epic-level status transitions still need tighter closeout hygiene.

## Concrete Action Items for `epic-mvp-04`
1. Add an epic-closeout checklist step that verifies parent epic status consistency before publishing sprint status updates.
2. For `mvp-04-1`, require deterministic structured error coverage for provider contract validation failures at adapter load/registration boundaries.
3. For `mvp-04-2`, add explicit fallback-policy regressions proving no implicit fallback on missing keys, failures, or timeouts unless configured.
4. Add a shared-boundary parity checklist for provider routing outputs so command and conversation paths expose consistent externally observable contract semantics.
5. Reuse sensitive-data regression templates for provider request/response metadata to ensure raw text remains excluded unless explicit opt-in exists.
6. Keep strict WSL `.venv` gate discipline as default for provider contract and fallback policy changes.

## Carry-Forward Guardrails
- Preserve deterministic behavior in all routing, provider contract, and observability boundaries.
- Keep safety-by-default as fail-fast behavior before side effects.
- Maintain command/conversation parity at shared externally observable boundaries.
- Treat raw request/response/conversation text as sensitive by default in persistence and telemetry.
- Continue strict WSL `.venv` quality gates for core runtime and contract stories.

## Recommended Sprint-Status Updates
1. `development_status.epic-mvp-03: in-progress -> done`
2. `development_status.epic-mvp-03-retrospective: optional -> done`
3. `last_updated: <set to current timestamp at update time>`
