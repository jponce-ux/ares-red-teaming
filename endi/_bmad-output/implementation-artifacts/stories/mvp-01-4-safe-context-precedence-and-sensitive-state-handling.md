# Story MVP-01.4: Safe Context Precedence and Sensitive-state Handling

Status: done

## Metadata
- **Story ID:** `MVP-01.4`
- **Story Key:** `mvp-01-4-safe-context-precedence-and-sensitive-state-handling`
- **Epic:** `EPIC-MVP-01` Core CLI, Routing, and Deterministic Runtime
- **Priority:** `P1`
- **Suggested Sprint:** `Sprint 2`
- **Type:** `Core Runtime + Security`

## Story
As a platform engineer, I want deterministic context resolution and safe persistence defaults, so that behavior is predictable and secrets are protected.

## Traceability
- **Functional Requirements:** `FR-006`
- **Architecture Constraints:** `ADR-007`, `ADR-010`, `ADR-011`, `ADR-019`

## Acceptance Criteria
1. Context precedence follows PRD order exactly: `explicit input -> command args/workflow inputs -> session -> project -> environment -> defaults`.
2. Sensitive values are redacted or excluded from persisted context and telemetry payloads.
3. Session persistence stores only non-sensitive interaction state by default.
4. Resolver behavior is deterministic across repeated runs with identical inputs.

### Clarification Addendum (2026-03-18)
- **Telemetry parity scope:** Structured telemetry safety controls apply to both command and conversation paths. Command dispatch must emit sanitized telemetry artifacts/events consistent with FR-007 observability coverage and AC-2 safety constraints.
- **Raw text sensitivity default:** Raw conversational/request/response text is treated as sensitive by default for persistence and telemetry. Durable/session snapshots and default telemetry payloads must exclude raw text unless an explicit, documented opt-in policy allows it.
- **Policy shape:** Safe-by-default behavior uses an allowlist-first payload design for persistence/telemetry fields; denylist-only key matching is insufficient for raw text safety guarantees.
- **Validation updates:** Tests must assert no raw-text leakage by default and verify correlation/event continuity for both command and conversation execution paths.

## Scope

### In Scope
- Add explicit, testable precedence resolution function(s) for context layers.
- Introduce a shared sensitive-value redaction/exclusion policy reusable by persistence and telemetry paths.
- Enforce safe-by-default persistence behavior for session context snapshots.
- Add strict-gate tests that prove precedence determinism and no secret leakage in persisted/telemetry outputs.

### Out of Scope
- External secrets manager integration.
- Cross-machine synchronization of context/session state.
- Changes to provider routing or capability authorization policy logic.

## Tasks / Subtasks
- [x] Define context precedence contract and merge policy (AC: 1, 4)
  - [x] Add explicit layer ordering constants/enums to avoid implicit merge order.
  - [x] Implement deterministic resolver function that accepts all context layers and returns resolved state.
  - [x] Ensure resolver is pure (no persistence/logging side effects).
- [x] Implement sensitive-field redaction/exclusion policy (AC: 2, 3)
  - [x] Define sensitive key detection strategy (exact keys + suffix/pattern safeguards).
  - [x] Provide reusable redaction utility for structured dict-like payloads.
  - [x] Guarantee excluded keys never appear in durable state and are masked in telemetry.
- [x] Integrate safe persistence defaults (AC: 2, 3)
  - [x] Apply redaction policy before any session context persistence write path.
  - [x] Persist only non-sensitive session interaction fields by default.
  - [x] Preserve deterministic ordering/serialization where relevant for stable tests.
- [x] Integrate telemetry safety hooks (AC: 2)
  - [x] Apply same redaction policy for emitted context-related observability events.
  - [x] Ensure correlation metadata remains intact while sensitive values are removed/masked.
- [x] Add strict-gate tests for determinism and safety (AC: 1, 2, 3, 4)
  - [x] Unit tests for precedence order and override behavior.
  - [x] Unit tests for redaction/exclusion patterns and edge cases.
  - [x] Integration tests proving persisted/telemetry payloads never leak sensitive values.

## Dev Notes

### Technical Requirements
- Preserve deterministic behavior guarantees used in existing runtime modules (`routing.py`, `workflow.py`, `conversation.py`): same inputs, same resolved outputs.
- Keep resolution and redaction logic composable and reusable by both persistence and observability consumers.
- Do not mutate input layer objects in-place; return resolved copies to avoid hidden side effects.
- Favor explicit allowlist/denylist decisions over heuristics-only secret handling.

### Architecture Compliance
- Respect ADR-007 separation: runtime context is ephemeral; durable storage is execution-history focused and must avoid secret persistence.
- Respect ADR-010 observability constraints: structured events stay traceable with correlation IDs while sensitive content is scrubbed.
- Respect ADR-019 bounded local retention intent by not expanding persisted session scope with sensitive blobs.
- Apply ADR-011 strict gate expectations for core runtime and security-adjacent behavior.

### Library / Framework Requirements
- Runtime implementation remains in Python `>=3.11`.
- Continue existing project dependencies and ranges from `pyproject.toml`:
  - `typer>=0.12,<1`
  - `rich>=13,<14`
  - `prompt-toolkit>=3.0,<4`
- Quality tooling expectations:
  - `pytest>=8,<9`
  - `mypy>=1.10,<2`
  - `ruff>=0.4,<1`

### File Structure Requirements
- Keep runtime changes within existing `src/endi/` module layout.
- If creating new context/redaction module(s), keep naming aligned with current style and avoid parallel duplicate runtime paths.
- Extend/add tests under `tests/` using existing `test_*.py` conventions and strict typing discipline.

### Testing Requirements (ADR-011)
- **Gate Level:** `Strict`
- Add deterministic precedence tests with repeated-run assertions for stable outputs.
- Add redaction tests covering:
  - known secret keys,
  - nested structures,
  - mixed sensitive/non-sensitive payloads,
  - telemetry and persistence outputs.
- Add regression tests ensuring no sensitive leakage while correlation/event structure remains valid.
- Run `ruff`, `mypy`, and `pytest` in WSL project `.venv`.

## Previous Story Intelligence (MVP-01.3)
- `src/endi/routing.py` and `src/endi/conversation.py` already enforce deterministic, structured runtime contracts; maintain this style for any context resolver outputs.
- Existing test suites emphasize explicit terminal states and structured envelopes; use the same pattern for context safety failures/assertions.
- Avoid introducing alternate entry paths that bypass centralized routing/runtime behavior.

## Git Intelligence
- Recent MVP-01 work shipped incrementally through dual-mode routing, deterministic lifecycle, and bounded conversational loop.
- Follow existing implementation cadence: add focused runtime primitives + strict tests, without broad architectural churn.

## Latest Tech Information
- No additional external libraries are required for this story.
- Prefer current dependency baseline and avoid version upgrades during this implementation.

## Dependencies
- Existing input classification/dispatch path (`src/endi/routing.py`) for consistent command/conversation behavior.
- Deterministic lifecycle patterns in `src/endi/workflow.py`.
- Existing bounded loop/runtime model in `src/endi/conversation.py` as reference for structured deterministic state handling.
- Persistence/observability follow-up stories in MVP-03 for full durable and telemetry expansion.

## References
- [Source: `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md`#Story MVP-01.4 — Safe context precedence and sensitive-state handling]
- [Source: `_bmad-output/planning-artifacts/endi-prd.md`#FR-006 Context Resolution and Safety]
- [Source: `_bmad-output/planning-artifacts/endi-prd.md`#7) Non-Functional Requirements]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#8. Context and Persistence Model]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#10. Observability Architecture]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#11. Testing and CI Quality Model]
- [Source: `_bmad-output/planning-artifacts/endi-adr-rationales.md`#ADR-007 — Context and State Storage]
- [Source: `_bmad-output/planning-artifacts/endi-adr-rationales.md`#ADR-010 — Observability Baseline]
- [Source: `_bmad-output/planning-artifacts/endi-adr-rationales.md`#ADR-019 — Local Retention Defaults]
- [Source: `_bmad-output/implementation-artifacts/stories/mvp-01-3-bounded-conversational-tool-loop.md`]
- [Source: `project-context.md`]
- [Source: `pyproject.toml`]

## Story Completion Note
Ultimate context engine analysis completed - comprehensive developer guide created.

## Dev Agent Record

### Agent Model Used
- Cascade (GPT-5)

### Debug Log References
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check ."`
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src/endi/context.py --fix"`
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy ."` (reported existing unrelated issues under `_bmad/...`)
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src/endi"`
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"`

### Completion Notes List
- Added `src/endi/context.py` with explicit `ContextLayer` precedence contract and deterministic `resolve_context_layers` merge behavior.
- Implemented shared sensitive-data policy (`is_sensitive_key`, `sanitize_for_persistence`, `sanitize_for_telemetry`) with nested payload handling and stable key ordering.
- Integrated resolver + sanitization into `dispatch_input` via context-layer parameters and safe artifacts (`resolved_context`, `session_snapshot`, `telemetry_payload`).
- Ensured safe persistence defaults by excluding sensitive fields in session snapshot generation.
- Ensured telemetry safety by redacting sensitive values while preserving correlation metadata.
- Added strict-gate tests for precedence determinism, deep-copy purity, command-input precedence, and no-leak session/telemetry behavior.
- Validation status: `ruff check .` passed, `mypy src/endi` passed, `pytest` passed (`39 passed`).
- Applied clarification addendum decisions: command-path telemetry parity, merged `command_context` precedence retention, and raw-text-safe defaults for persistence/telemetry payloads.
- Final validation status: `ruff check .` passed, `mypy src/endi` passed, `pytest` passed (`40 passed`).

### File List
- `src/endi/context.py`
- `src/endi/routing.py`
- `tests/test_dual_mode_routing.py`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Change Log
- 2026-03-18: Implemented deterministic context precedence and sensitive-state safety controls; integrated safe session/telemetry artifacts and added strict validation tests.
- 2026-03-18: Finalized MVP-01.4 with telemetry parity and raw-text-safe default handling updates; completed lint/type/test verification and moved story to `done`.
