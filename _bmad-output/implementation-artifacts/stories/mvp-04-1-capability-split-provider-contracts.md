# Story MVP-04.1: Capability-split Provider Contracts

Status: done

## Metadata
- **Story ID:** `MVP-04.1`
- **Story Key:** `mvp-04-1-capability-split-provider-contracts`
- **Epic:** `EPIC-MVP-04` Provider Capability Layer and Default Routing
- **Priority:** `P1`
- **Suggested Sprint:** `Sprint 3`
- **Type:** `Provider Contract Core`

## Story
As a platform architect, I want separate provider interfaces by capability, so that adapters evolve without lowest-common-denominator coupling.

## Objective
Establish a deterministic, provider-independent capability contract layer for chat, embeddings, and tool-calling with load-time registration validation and structured contract errors that are stable across command/conversation shared boundaries.

## Traceability
- **Functional Requirements:** `FR-004`
- **Architecture Constraints:** `ADR-008`, `ADR-009`, `ADR-013`, `ADR-011`

## Scope

### In Scope
- Define first-class capability contracts: `ChatProvider`, `EmbeddingProvider`, and `ToolCallingProvider`.
- Add registration/load-time contract validation for provider adapters.
- Implement deterministic structured contract-failure envelopes for malformed or incompatible adapters.
- Ensure provider selection/consumption paths can use capability interfaces without vendor-specific coupling at shared runtime boundaries.
- Add strict-gate tests for valid/invalid registration, version compatibility checks, and deterministic error outputs.

### Out of Scope
- Implementation of concrete provider adapters and fallback routing policy behavior (covered by `MVP-04.2`).
- Non-v1 capability contracts (vision, speech, multimodal beyond current scope).
- Provider performance tuning, retries, or dynamic fallback heuristics.

## Acceptance Criteria
1. **Capability split contracts:** Runtime exposes distinct typed contracts for `ChatProvider`, `EmbeddingProvider`, and `ToolCallingProvider`, each with explicit required operations and no cross-capability mandatory methods.
2. **Registration/load-time validation:** Adapter registration validates capability conformance and required metadata/version fields at registration/load time before adapter use.
3. **Contract failure determinism:** Invalid provider contracts fail fast with deterministic structured errors containing stable `code`, `message`, and machine-readable `details` (including missing/invalid fields and capability information).
4. **Compatibility enforcement:** Capability contract version compatibility is validated at load-time with hard-fail behavior for incompatible versions.
5. **Provider-independence boundary:** Runtime-facing consumption paths can resolve capabilities by contract type rather than vendor-specific branching.
6. **Shared-boundary parity safety:** Any surfaced contract failure format remains consistent at command/conversation shared boundaries and preserves sensitive-by-default handling.

## Tasks / Subtasks
- [x] Define capability contract models and shared status/error schema (AC: 1, 3)
  - [x] Introduce dedicated provider contract types for chat, embeddings, and tool-calling in `src/endi/`.
  - [x] Mirror deterministic structured contract-result patterns already used in runtime/tool contracts (`status`, `status_code`, structured `error`).
- [x] Implement provider registration and load-time validator (AC: 2, 3, 4)
  - [x] Add deterministic validation for required methods/fields per capability contract.
  - [x] Validate contract version metadata and return deterministic incompatibility errors.
  - [x] Reject non-conformant providers before runtime execution paths can consume them.
- [x] Integrate capability-based provider resolution boundary (AC: 1, 5, 6)
  - [x] Ensure provider consumption points use capability abstraction instead of direct vendor checks.
  - [x] Preserve command/conversation parity at externally observable shared error boundaries.
- [x] Add strict regression coverage (AC: 1, 2, 3, 4, 5, 6)
  - [x] Positive tests for valid registration across each capability contract type.
  - [x] Negative tests for missing methods/fields, invalid metadata, and version incompatibility.
  - [x] Determinism tests proving stable structured error shape for equivalent invalid inputs.
  - [x] Parity/sanitization checks where contract failures surface through shared runtime paths.

## Dev Notes

### Technical Requirements
- Preserve deterministic behavior: identical invalid inputs must produce stable contract-failure codes/details ordering.
- Preserve safety-by-default: do not leak raw provider request/response text in validation or error metadata.
- Follow existing structured contract error patterns from `src/endi/tools.py` and `src/endi/persistence.py` (deterministic code + details payload).
- Keep command/conversation parity on shared externally observable boundaries already enforced in routing/tests.
- Keep provider contract layer capability-first and additive for future contracts (no lowest-common-denominator interface).

### Implementation Notes Aligned with Existing `src/endi` Patterns
- Reuse deterministic typed-envelope style already present in `ToolResult`/`ToolStatusCode` style contracts.
- Reuse fail-fast registration semantics and missing/invalid field reporting conventions established in `ToolRegistry.register`.
- Preserve routing/runtime error surfacing conventions in `src/endi/routing.py` for structured error component/code/status_code propagation.
- Keep module organization consistent with existing focused domain modules under `src/endi/` and focused tests under `tests/`.

### Concrete File-level Guidance
- `src/endi/providers.py` (new): capability interfaces, provider contract status codes, deterministic contract error/result envelopes, registration/load-time validator.
- `src/endi/routing.py` (update only if needed): shared-boundary error mapping/parity for provider contract failures.
- `tests/test_provider_contracts.py` (new): capability conformance tests, load-time validation failures, deterministic error regressions.
- `tests/test_dual_mode_routing.py` (targeted updates if needed): parity assertions for surfaced provider contract failures at shared command/conversation boundaries.

### Testing Requirements (Strict Gate)
- **Gate Level:** `Strict`
- Execute quality gates in WSL project `.venv`:
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && ruff check src tests"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && mypy src"`
  - `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"`
- Required test focus:
  - Contract conformance coverage per capability: `ChatProvider`, `EmbeddingProvider`, `ToolCallingProvider`.
  - Registration/load-time validation and deterministic structured error coverage.
  - Version-compatibility hard-fail coverage.
  - Shared-boundary parity and sensitive-by-default regression coverage for surfaced failures.

### Review-Ready Exit Conditions
- [x] All acceptance criteria are covered by explicit automated tests.
- [x] Each capability contract type has positive + negative conformance coverage.
- [x] Registration/load-time validation rejects invalid contracts deterministically.
- [x] Structured contract-failure envelopes are stable and machine-parseable.
- [x] No command/conversation parity regression at shared externally observable boundaries.
- [x] No sensitive free-form text leakage in provider contract error metadata.

## Dependencies
- Existing deterministic contract/error conventions in `src/endi/tools.py`.
- Existing structured runtime error propagation/parity patterns in `src/endi/routing.py` and `tests/test_dual_mode_routing.py`.
- Follow-on story `mvp-04-2-initial-adapters-and-explicit-fallback-behavior` for concrete provider adapter and fallback behavior implementation.

## References
- [Source: `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md`#EPIC-MVP-04: Provider Capability Layer and Default Routing]
- [Source: `_bmad-output/planning-artifacts/endi-epics-stories-backlog.md`#Story MVP-04.1 — Capability-split provider contracts]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#2. Architecture Principles (Locked)]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#9. Provider Architecture]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#11. Testing and CI Quality Model]
- [Source: `_bmad-output/planning-artifacts/endi-architecture-final.md`#13. Versioning and Compatibility]
- [Source: `src/endi/tools.py`]
- [Source: `src/endi/routing.py`]
- [Source: `tests/test_tool_contract.py`]
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
- `wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi bash -lc "source .venv/bin/activate && pytest"` (pass, 106 passed)

### Completion Notes List
- Implemented `src/endi/providers.py` with split capability contracts (`ChatProvider`, `EmbeddingProvider`, `ToolCallingProvider`), structured provider contract envelopes, and deterministic registry validation.
- Added load-time contract checks for required metadata fields, capability conformance by protocol, and hard-fail version compatibility validation.
- Implemented capability-based resolution APIs (`resolve_chat_provider`, `resolve_embedding_provider`, `resolve_tool_calling_provider`) without vendor-specific branching.
- Updated `src/endi/routing.py` parity surfaces for provider contract failures: deterministic workflow status-code mapping and sanitized conversation telemetry `provider_contract` payload extraction.
- Added strict regression coverage in `tests/test_provider_contracts.py` and targeted parity/sanitization coverage in `tests/test_dual_mode_routing.py`.
- Executed strict WSL `.venv` gates successfully: `ruff check src tests`, `mypy src`, `pytest`.
- Post-review hardening: enforced fail-fast invalid metadata rejection for typed `ProviderAdapterContract` registrations and added routing extraction fallback from `provider_name` to `identifier` for provider parity payloads.
- Added focused regressions for typed metadata rejection and `provider_not_found` identifier fallback parity; re-ran strict WSL `.venv` gates (`ruff`, `mypy`, `pytest`) with `108 passed`.

### File List
- `src/endi/providers.py`
- `src/endi/routing.py`
- `tests/test_provider_contracts.py`
- `tests/test_dual_mode_routing.py`
- `_bmad-output/implementation-artifacts/stories/mvp-04-1-capability-split-provider-contracts.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

### Change Log
- 2026-03-24: Closed review findings by hardening typed registration validation and provider identity parity extraction; added focused regressions and re-ran strict gates; story moved to done.
- 2026-03-24: Implemented MVP-04.1 provider capability-split contracts, deterministic registration/version validation, provider parity surfacing updates, and strict test coverage; gates passed and story moved to review.
- 2026-03-24: Rebuilt MVP-04.1 story as implementation-ready create-story artifact with explicit capability-split contract requirements and strict quality gates.
