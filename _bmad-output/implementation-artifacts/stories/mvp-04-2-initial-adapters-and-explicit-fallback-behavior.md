# Story MVP-04.2: Initial Adapters and Explicit Fallback Behavior

Status: done

## Metadata
- **Story ID:** `MVP-04.2`
- **Story Key:** `mvp-04-2-initial-adapters-and-explicit-fallback-behavior`
- **Epic:** `EPIC-MVP-04` Provider Capability Layer and Default Routing
- **Priority:** `P1`
- **Suggested Sprint:** `Sprint 3`
- **Type:** `Provider Adapter Implementation + Fallback Policy Enforcement`

## Story
As a runtime user, I want stable defaults and explicit local fallback behavior, so that model routing is predictable.

## Objective
Implement v1 provider adapter defaults and explicit-only local fallback behavior so that routing outcomes are deterministic, auditable, and consistent across command and conversational execution boundaries.

## Traceability
- **Functional Requirements:** `FR-003`, `FR-004`
- **Architecture Constraints:** `ADR-008`, `ADR-009`, `ADR-015`, `ADR-016`, `ADR-011`

## Scope

### In Scope
- Configure and enforce default provider selections:
  - chat = `openai:gpt-4o-mini`
  - tools = `anthropic:claude-3.7-sonnet`
  - embeddings = `openai:text-embedding-3-large`
- Register `ollama` as local fallback provider with explicit-only policy behavior.
- Enforce no silent/automatic fallback on missing credentials, provider failures, or timeouts unless explicitly enabled by user/config.
- Surface deterministic routing/fallback telemetry metadata for observability and audit reconstruction.
- Preserve compatibility with capability-split contracts introduced in `MVP-04.1`.

### Out of Scope
- Automatic dynamic fallback heuristics, provider cascading, or retry trees.
- Provider-level optimization tuning (latency/cost scoring, adaptive retries).
- New capability contracts beyond chat/tool-calling/embeddings.

## Acceptance Criteria
1. **Locked default routing:** Runtime uses v1 defaults exactly as defined in architecture (`chat=openai:gpt-4o-mini`, `tools=anthropic:claude-3.7-sonnet`, `embeddings=openai:text-embedding-3-large`).
2. **Explicit-only local fallback:** `ollama` local fallback path is available only when explicitly requested through config/flag/context.
3. **No silent fallback by default:** Missing API keys, adapter initialization failures, or provider timeouts do not trigger automatic fallback in default mode.
4. **Deterministic failure contracts:** Default-mode fallback blocks emit deterministic structured errors with stable `code`, `component`, `status_code`, and machine-readable details.
5. **Command/conversation parity at shared boundaries:** Equivalent routing/fallback inputs produce equivalent externally observable contract outcomes across command and conversation paths (conversation may include additional loop metadata, but shared failure semantics must match).
6. **Sensitive-by-default handling:** Telemetry and persisted metadata must not expose raw provider request/response text or secrets unless explicitly opted in through approved mechanisms.
7. **Auditability:** Routing selection and fallback decision state are captured in structured metadata/events sufficient for run reconstruction.

## Acceptance Criteria Traceability
- **AC1** ← `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md` `Story MVP-04.2` + `_bmad-output/planning-artifacts/endi-architecture-final.md` §9.3 Default Routing.
- **AC2** ← backlog `Story MVP-04.2` + architecture §9.2 Initial Provider Set, §9.3 Default Routing.
- **AC3** ← backlog `Story MVP-04.2` + architecture §9.4 Fallback Policy, ADR-016.
- **AC4** ← deterministic contract/error conventions carried from `MVP-01.5` and `MVP-04.1` runtime patterns.
- **AC5** ← command/conversation parity guardrails from prior runtime stories (`MVP-01.5`, `MVP-02.x`, `MVP-03.x`) and shared-boundary expectations.
- **AC6** ← sensitive-by-default project/runtime policy (`project-context.md`, existing `routing.py` sanitization conventions).
- **AC7** ← observability baseline and structured telemetry requirements (`MVP-03.x`, architecture ADR-010/011 alignment).

## Tasks / Subtasks
- [x] Implement default adapter routing configuration (AC: 1)
  - [x] Add deterministic config resolution for chat/tools/embeddings defaults with stable precedence behavior.
  - [x] Ensure defaults are vendor-qualified identifiers and validated before execution.
- [x] Implement explicit-only local fallback controls (AC: 2, 3)
  - [x] Add config/context flag handling for explicit local fallback enablement.
  - [x] Ensure fallback remains disabled when explicit mode is not enabled.
- [x] Enforce no-silent-fallback failure path (AC: 3, 4)
  - [x] Convert missing-key/provider-failure/timeout cases into deterministic structured fallback-block errors.
  - [x] Preserve fail-fast behavior and avoid hidden second-attempt provider routing.
- [x] Add routing/fallback observability metadata (AC: 5, 6, 7)
  - [x] Capture selected provider, fallback mode, fallback eligibility, and fallback decision outcome.
  - [x] Ensure metadata sanitization excludes sensitive free-text and secret-bearing keys.
- [x] Add focused tests for adapter + fallback policy behavior (AC: 1-7)
  - [x] Positive tests for default routing and explicit fallback-enabled routing.
  - [x] Negative tests proving no fallback in default mode across missing key/failure/timeout scenarios.
  - [x] Parity tests for shared command/conversation fallback outcomes.
  - [x] Sanitization regression tests for routing/fallback telemetry payloads.

## Dev Notes

### Technical Requirements
- Keep fallback policy deterministic and safety-by-default: explicit enablement only.
- Reuse structured contract failure shapes already used in `src/endi/routing.py`, `src/endi/tools.py`, and `src/endi/providers.py`.
- Keep compatibility with capability-split provider interfaces from `MVP-04.1`; no lowest-common-denominator coupling.
- Preserve externally observable command/conversation parity for shared provider-routing contract outcomes.
- Preserve sensitive-by-default behavior for raw input/output text and credential-adjacent fields.

### Implementation Notes Aligned with Existing `src/endi` Patterns
- Provider contracts and registration behavior are established in `src/endi/providers.py`; this story adds default adapter wiring and fallback policy behavior on top.
- Routing/telemetry parity extraction conventions already exist in `src/endi/routing.py`; extend rather than fork semantics.
- Keep deterministic result/error `status_code` mapping stable for equivalent fallback-policy outcomes.

### Concrete File-level Guidance
- `src/endi/providers.py`: extend adapter/default selection and explicit-only fallback policy mechanics as needed.
- `src/endi/routing.py`: ensure shared-boundary surfacing/parity of provider routing and fallback failure semantics.
- `tests/test_provider_contracts.py`: add adapter/default/fallback policy behavior tests at provider boundary.
- `tests/test_dual_mode_routing.py`: add command/conversation parity + sanitization regressions for fallback decisions.

### Testing Requirements (Moderate + Strict Gates)
- **Gate Levels:** `Moderate` for adapter implementation behavior, `Strict` for fallback-policy correctness and shared-boundary parity.
- Execute quality gates in WSL project `.venv`:
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src tests"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"`
- Required test focus:
  - Default provider selection correctness.
  - Explicit-only fallback enforcement for missing key/failure/timeout classes.
  - Deterministic structured failure contracts.
  - Command/conversation parity at shared externally observable boundaries.
  - Sensitive-by-default telemetry/persistence sanitization.

### Review-Ready Exit Conditions
- [x] All acceptance criteria are covered by explicit automated tests.
- [x] Default provider routing is stable and deterministic.
- [x] No automatic silent fallback occurs in default mode.
- [x] Explicit local fallback works only when enabled.
- [x] Shared command/conversation fallback outcomes preserve parity.
- [x] Sensitive text/secrets are excluded by default from fallback telemetry/persistence.

## Dependencies
- `mvp-04-1-capability-split-provider-contracts` (done): capability contracts + validation baseline.
- Existing deterministic runtime error/telemetry patterns in `src/endi/routing.py`.
- Existing provider registry/contracts in `src/endi/providers.py`.

## References
- [Source: `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md`#EPIC-MVP-04: Provider Capability Layer and Default Routing]
- [Source: `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md`#Story MVP-04.2 — Initial adapters and explicit fallback behavior]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#9. Provider Architecture]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#9.3 Default Routing (v1)]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#9.4 Fallback Policy]
- [Source: `project-context.md`#Execution Environment]
- [Source: `project-context.md`#Agent Command Rules]

## Story Completion Note
Ultimate context engine analysis completed - comprehensive developer guide created.

## Dev Agent Record

### Agent Model Used
- Cascade (GPT-5)

### Debug Log References
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src tests"` (pass)
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"` (pass)
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"` (pass, 117 passed)

### Completion Notes List
- Implemented deterministic v1 provider routing defaults in `src/endi/providers.py` for chat/tool-calling/embeddings with vendor-qualified override validation and explicit-only local fallback policy metadata.
- Added explicit local fallback policy evaluation in `src/endi/providers.py` with deterministic structured outcomes for `missing_credentials`, `provider_failure`, and `timeout`, blocking by default unless explicitly enabled.
- Updated `src/endi/routing.py` to map `provider_fallback_blocked` into deterministic `invalid_contract` status behavior and to surface parity-safe provider metadata (`provider_routing`, `provider_fallback`) in command and conversation telemetry paths.
- Added runtime-path fallback-policy normalization in `src/endi/routing.py` so real command execution provider failures (`provider_failure`, `missing_credentials`, `timeout`) are deterministically normalized to `provider_fallback_blocked` when explicit local fallback is not enabled.
- Preserved sensitive-by-default behavior by sanitizing fallback payload extraction through existing raw-text field filtering and safe telemetry envelope building.
- Added focused provider-boundary tests in `tests/test_provider_contracts.py` and shared-boundary parity/sanitization tests in `tests/test_dual_mode_routing.py` covering defaults, explicit-only fallback, deterministic failure contracts, command/conversation parity, and runtime-path fallback normalization.

### File List
- `src/endi/providers.py`
- `src/endi/routing.py`
- `tests/test_provider_contracts.py`
- `tests/test_dual_mode_routing.py`
- `_bmad-output/implementation-artifacts/stories/mvp-04-2-initial-adapters-and-explicit-fallback-behavior.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Change Log
- 2026-03-24: Implemented MVP-04.2 initial adapter defaults and explicit-only fallback policy behavior; added deterministic fallback contract mapping and provider routing/fallback telemetry parity across command/conversation; added focused tests; quality gates passed; story moved to review.
- 2026-03-24: Completed post-review hardening by enforcing explicit fallback policy in the real command runtime failure path, adding missing AC3 reason-matrix coverage, and rerunning strict WSL `.venv` quality gates (`ruff`, `mypy`, `pytest` with 117 passed).
- 2026-03-24: Refreshed story into implementation-ready create-story format with explicit acceptance traceability, deterministic/safety guardrails, parity and sensitive-by-default expectations, and strict WSL `.venv` quality gates.
