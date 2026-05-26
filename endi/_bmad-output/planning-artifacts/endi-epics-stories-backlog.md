# ENDI Epics and User Stories Backlog

## 1) Scope and Constraints
- Inputs used:
  - `_bmad-output/planning-artifacts/endi-prd.md`
  - `_bmad-output/planning-artifacts/endi-architecture-final.md`
  - `_bmad-output/planning-artifacts/endi-adr-rationales.md`
- Delivery order: **MVP first**, then **post-MVP expansion**.
- Architecture constraint: stories are aligned to locked `ADR-001` through `ADR-019` and avoid conflicting implementation paths.
- Test strategy constraint (`ADR-011`):
  - **Strict gates:** core/runtime/security/persistence/provider contracts
  - **Moderate gates:** provider adapters
  - **Light gates:** plugins/experimental adapters

## 2) Epic Overview (Prioritized)
### MVP Epics
1. **EPIC-MVP-00: Delivery Foundation and Greenfield Bootstrap**
2. **EPIC-MVP-01: Core CLI, Routing, and Deterministic Runtime**
3. **EPIC-MVP-02: Safety, Permissions, and Human-in-the-Loop Controls**
4. **EPIC-MVP-03: Persistence and Observability Baseline**
5. **EPIC-MVP-04: Provider Capability Layer and Default Routing**
6. **EPIC-MVP-05: Terminal UX & Operator Experience (Terminal-native)**

### Post-MVP Epics
7. **EPIC-POST-01: Plugin Ecosystem and Compatibility Controls**
8. **EPIC-POST-02: Advanced Orchestration and Extension Tracks**

## 3) MVP Epics and Stories

## EPIC-MVP-00: Delivery Foundation and Greenfield Bootstrap
**Goal:** Establish a runnable project skeleton and CI quality baseline before feature implementation.
**Primary FR coverage:** `FR-002`, `FR-007`
**Key ADR constraints:** `ADR-001`, `ADR-002`, `ADR-011`

### Story MVP-00.1 — Repository scaffold and CI quality baseline
- **As a** maintainer, **I want** a greenfield scaffold and CI baseline, **so that** feature stories build on a stable, testable delivery foundation.
- **Traceability:** `FR-002`, `FR-007`
- **Acceptance Criteria:**
  - Project skeleton is created with source/tests layout and baseline Python project configuration for ENDI runtime development.
  - CI pipeline runs lint (`ruff`), type-check (`mypy`), and tests (`pytest`) on pull requests.
  - CI reports stage-specific failures clearly (lint, type-check, test) and blocks merge on failed strict-gate checks.
  - Baseline quality-gate configuration is documented and aligned to ADR-011 tiering for core MVP stories.
- **Testing Notes:** **Strict gate** (delivery foundation). Add CI smoke validation for pass/fail behavior and reporting.

## EPIC-MVP-01: Core CLI, Routing, and Deterministic Runtime
**Goal:** Implement terminal-native dual interaction model and deterministic workflow core.
**Primary FR coverage:** `FR-001`, `FR-002`, `FR-003`, `FR-004`, `FR-006`, `FR-009`
**Key ADR constraints:** `ADR-001`, `ADR-002`, `ADR-003`, `ADR-004`, `ADR-012`

### Story MVP-01.1 — Dual-mode CLI entry and input classifier
- **As a** terminal operator, **I want** `/command` and free-text inputs to be classified reliably, **so that** command and conversational paths route correctly.
- **Traceability:** `FR-001`, `FR-009`
- **Acceptance Criteria:**
  - `/`-prefixed input routes to command workflow path.
  - Non-prefixed input routes to conversational path.
  - Invalid command syntax returns structured non-executing validation errors.
- **Testing Notes:** **Strict gate** (core router/runtime). Add unit tests for classification and integration tests for route outcomes.

### Story MVP-01.2 — Deterministic workflow lifecycle engine
- **As a** workflow author, **I want** fixed lifecycle stages, **so that** execution is reproducible and auditable.
- **Traceability:** `FR-002`
- **Acceptance Criteria:**
  - Lifecycle stages execute in order: initialize, validate, plan(optional), execute, collect, output, finalize.
  - Required input validation fails fast before execution.
  - Structured output includes status, payload, and metadata.
- **Testing Notes:** **Strict gate** (core runtime contract). Add state-transition and failure-mode tests.

### Story MVP-01.3 — Bounded conversational tool loop
- **As a** user, **I want** conversational orchestration with bounded tool iterations, **so that** responses are useful and controlled.
- **Traceability:** `FR-003`
- **Acceptance Criteria:**
  - Agent loop supports select-action -> execute-tool -> observe-result cycles.
  - Max iteration limits are configurable per agent/workflow.
  - Final output references tool outputs used in synthesis.
- **Testing Notes:** **Strict gate** (agent runtime controls). Add loop-bound, timeout, and reference-integrity tests.

### Story MVP-01.4 — Safe context precedence and sensitive-state handling
- **As a** platform engineer, **I want** deterministic context resolution and safe persistence defaults, **so that** behavior is predictable and secrets are protected.
- **Traceability:** `FR-006`
- **Acceptance Criteria:**
  - Context precedence follows PRD order: explicit input -> args/workflow input -> session -> project -> environment -> defaults.
  - Sensitive values are redacted or excluded from persisted context.
  - Session persistence stores only non-sensitive interaction state by default.
- **Testing Notes:** **Strict gate** (security + context model). Add precedence and redaction tests.

### Story MVP-01.5 — Tool contract standardization baseline
- **As a** runtime engineer, **I want** all tools to follow a single validated contract, **so that** invocation behavior is deterministic and safe across command and agent paths.
- **Traceability:** `FR-004`
- **Acceptance Criteria:**
  - Tool registry rejects tool registration when required metadata or contract fields are missing or malformed; invalid tools never enter active registry state.
  - Tool invocation validates input against declared schema before execution and blocks handler side effects when validation fails.
  - Tool execution returns structured success/error responses with deterministic status codes for success, invalid contract, invalid input, not found, and execution error outcomes.
  - Command and conversational runtime surfaces preserve the same tool contract semantics at externally observable boundaries: identical validation behavior, deterministic status mapping, and structured tool error code/component details when tool invocation fails (conversation may also include loop-level termination reason).
- **Testing Notes:** **Strict gate** (core tool contract). Add registry validation, schema enforcement, deterministic response-shape tests, and cross-path runtime parity tests at dispatch/conversation surfaces (not only registry utility calls).

## EPIC-MVP-02: Safety, Permissions, and Human-in-the-Loop Controls
**Goal:** Enforce capability permissions, confirmation gates, and policy-driven backend isolation.
**Primary FR coverage:** `FR-005`, `FR-010`
**Key ADR constraints:** `ADR-006`, `ADR-017`, `ADR-018`, `ADR-004`, `ADR-012`

### Story MVP-02.1 — Capability authorization enforcement layer
- **As a** security/compliance engineer, **I want** sensitive operations blocked without required capability, **so that** unauthorized actions cannot execute.
- **Traceability:** `FR-005`, `FR-010`
- **Acceptance Criteria:**
  - Sensitive capability checks run before command/workflow/tool execution.
  - Missing permission returns explicit structured denial error.
  - Denied operations do not execute any side-effecting tool step.
- **Testing Notes:** **Strict gate** (security policy enforcement). Add deny/allow matrix tests by capability.

### Story MVP-02.2 — Per-action confirmation for sensitive capabilities
- **As an** operator, **I want** explicit confirmation for high-impact actions, **so that** destructive behavior cannot run autonomously.
- **Traceability:** `FR-005`, `FR-010`
- **Acceptance Criteria:**
  - Sensitive capabilities require explicit per-action confirmation by default.
  - High-impact summary is shown before confirmation.
  - Confirmation decision is linked to execution ID in audit records.
- **Testing Notes:** **Strict gate** (HITL safety path). Add confirmation required/declined/approved flow tests.

### Story MVP-02.3 — `--approve-plan` execution mode for trusted automation
- **As a** CI/operator user, **I want** one upfront approval for planned sensitive actions, **so that** safe automation can run non-interactively.
- **Traceability:** `FR-005`, `FR-010`
- **Acceptance Criteria:**
  - `--approve-plan` captures and confirms planned sensitive action set once.
  - `--approve-plan --non-interactive` executes only when plan is fully approved.
  - Actions outside approved plan are blocked and reported.
- **Testing Notes:** **Strict gate** (safety policy variant). Add planned-vs-actual drift tests.

### Story MVP-02.4 — Capability-to-backend mapping and isolation resolver
- **As a** runtime maintainer, **I want** explicit capability backend routing, **so that** high-risk actions use stronger isolation.
- **Traceability:** `FR-005`
- **Acceptance Criteria:**
  - Runtime uses explicit capability->backend mapping table for backend selection.
  - Highest isolation requirement wins when multiple capabilities are requested.
  - v1 ships with `LocalBackend` implementation and interface contracts for worker/container/remote backends.
- **Testing Notes:** **Strict gate** (runtime/security boundary). Add policy resolution tests and backend selection contract tests.

## EPIC-MVP-03: Persistence and Observability Baseline
**Goal:** Deliver local durable execution history and traceable structured telemetry.
**Primary FR coverage:** `FR-007`, `FR-002`, `FR-010`
**Key ADR constraints:** `ADR-007`, `ADR-010`, `ADR-019`

### Story MVP-03.1 — SQLite execution history schema and write path
- **As an** SRE, **I want** durable run history, **so that** I can audit and diagnose workflow outcomes.
- **Traceability:** `FR-007`, `FR-002`
- **Acceptance Criteria:**
  - SQLite stores sessions, commands, workflows, steps, tool calls, status, timing metadata.
  - Writes are atomic per execution stage transition.
  - Query path can reconstruct a complete run timeline.
- **Testing Notes:** **Strict gate** (persistence contract). Add schema, migration, and reconstruction tests.

### Story MVP-03.2 — Structured JSON logs with baseline correlation hierarchy
- **As an** operator, **I want** end-to-end correlated logs, **so that** failures can be traced quickly.
- **Traceability:** `FR-007`
- **Acceptance Criteria:**
  - Events include correlation IDs, component, action, status, duration, timestamp.
  - Baseline correlation chain supports session -> command -> workflow -> step.
  - Errors include failure type and component level.
- **Testing Notes:** **Strict gate** (observability baseline). Add event-schema and baseline correlation continuity tests.

### Story MVP-03.4 — Extended correlation for conversational tool path
- **As an** SRE, **I want** correlated agent and tool-call telemetry, **so that** conversational executions can be reconstructed end-to-end.
- **Traceability:** `FR-007`
- **Acceptance Criteria:**
  - When conversational/agent execution is enabled, correlation chain extends to session -> command -> workflow -> step -> agent -> tool_call.
  - Agent and tool_call events include valid parent identifiers linking back to workflow/step context.
  - Missing or broken parent linkage is surfaced as structured observability validation failure.
- **Testing Notes:** **Strict gate** (observability contract extension). Add conversational path correlation and parent-link integrity tests.

### Story MVP-03.3 — Retention and auto-prune policy implementation
- **As a** workstation owner, **I want** bounded local storage, **so that** ENDI history does not grow unbounded.
- **Traceability:** `FR-007`
- **Acceptance Criteria:**
  - Retention defaults are 30 days or 2 GB, with auto-prune enabled.
  - Pruning occurs by age first, then oldest-run deletion until size threshold is met.
  - Prune actions are logged with affected record counts/artifact references.
- **Testing Notes:** **Strict gate** (persistence reliability). Add retention simulation tests.

## EPIC-MVP-04: Provider Capability Layer and Default Routing
**Goal:** Provide provider-independent contracts and v1 default provider behavior.
**Primary FR coverage:** `FR-003`, `FR-004`
**Key ADR constraints:** `ADR-008`, `ADR-009`, `ADR-015`, `ADR-016`

### Story MVP-04.1 — Capability-split provider contracts
- **As a** platform architect, **I want** separate provider interfaces by capability, **so that** adapters evolve without lowest-common-denominator coupling.
- **Traceability:** `FR-004`
- **Acceptance Criteria:**
  - Implement `ChatProvider`, `EmbeddingProvider`, and `ToolCallingProvider` interfaces.
  - Enforce capability contract validation at adapter registration/load time.
  - Provider contract failures produce deterministic structured errors.
- **Testing Notes:** **Strict gate** (provider contract core). Add interface compliance tests.

### Story MVP-04.2 — Initial adapters and explicit fallback behavior
- **As a** runtime user, **I want** stable defaults and explicit local fallback behavior, **so that** model routing is predictable.
- **Traceability:** `FR-003`, `FR-004`
- **Acceptance Criteria:**
  - Configure defaults: chat=`openai:gpt-4o-mini`, tools=`anthropic:claude-3.7-sonnet`, embeddings=`openai:text-embedding-3-large`.
  - Include `ollama` as local fallback provider in explicit-only mode.
  - No automatic fallback occurs on missing keys/failures/timeouts unless explicitly enabled by user/config.
- **Testing Notes:** **Moderate gate** (provider adapters) + **Strict gate** (fallback policy checks).

## EPIC-MVP-05: Terminal UX & Operator Experience (Terminal-native)
**Goal:** Improve readability, command discoverability, and operator confidence in terminal-only UX.
**Primary FR coverage:** `FR-001`, `FR-009`, `FR-010`
**Key ADR constraints:** `ADR-002`, `ADR-018`

### Story MVP-05.1 — Rich terminal theming and readability baseline
- **As a** daily CLI user, **I want** clear visual hierarchy and status rendering, **so that** I can parse results quickly under pressure.
- **Traceability:** `FR-009`
- **Acceptance Criteria:**
  - Command outcomes, warnings, confirmations, and errors use consistent Rich styles/panels.
  - Rendering is validated in at least three terminal/theme environments: one dark 256-color profile, one light profile, and one low-color profile.
  - For each environment, warning/error/confirmation states remain distinguishable without relying on color alone.
  - Critical actions have visually distinct summaries before confirmation.
- **Testing Notes:** **Moderate gate** (presentation-focused UX) with snapshot checks for warning/error/confirmation/critical-summary states across the defined terminal/theme matrix.

### Story MVP-05.2 — Help, examples, and command introspection
- **As a** new operator, **I want** discoverable commands and usage examples, **so that** I can self-serve workflows.
- **Traceability:** `FR-009`, `FR-001`
- **Acceptance Criteria:**
  - `help` output includes command descriptions, argument schema, and examples.
  - Invalid invocations return actionable hints and nearest valid command suggestions.
  - Introspection output lists command primary execution target.
- **Testing Notes:** **Strict gate** (command spec compliance). Add help contract and validation error UX tests.

### Story MVP-05.3 — Confirmation UX and operation summary consistency
- **As an** incident responder, **I want** concise, standardized pre-execution summaries, **so that** I can approve high-impact actions with confidence.
- **Traceability:** `FR-010`, `FR-005`
- **Acceptance Criteria:**
  - Sensitive operations render normalized summary fields: intent, targets, capabilities, backend, risk level.
  - Summary format is consistent across command/workflow/agent-triggered sensitive actions.
  - Audit log links summary shown to final confirmation decision.
- **Testing Notes:** **Strict gate** (safety UX contract). Add summary-schema and consistency tests.

## 4) Post-MVP Epics and Stories

## EPIC-POST-01: Plugin Ecosystem and Compatibility Controls
**Goal:** Extend ENDI without core modifications using validated plugin contracts.
**Primary FR coverage:** `FR-008`, `FR-004`, `FR-009`
**Key ADR constraints:** `ADR-005`, `ADR-013`

### Story POST-01.1 — Dual-source plugin discovery and registration
- **As a** platform extender, **I want** local manifest and package entry-point plugin discovery, **so that** I can add capabilities without core edits.
- **Traceability:** `FR-008`
- **Acceptance Criteria:**
  - Loader discovers plugins from `~/.endi/plugins` and `entry_points(group="endi.plugins")`.
  - Registration supports commands/workflows/agents/tools via unified contract.
  - Invalid plugin manifests are rejected with explicit diagnostics.
- **Testing Notes:** **Light gate** (plugin path) with contract smoke tests.

### Story POST-01.2 — Plugin capability version checks at load time
- **As a** maintainer, **I want** compatibility checks before plugin activation, **so that** incompatible extensions fail safely.
- **Traceability:** `FR-008`
- **Acceptance Criteria:**
  - Plugin load validates core SemVer and capability contract versions.
  - Incompatible plugins hard-fail at load with remediation guidance.
  - Deprecation warnings include removal target versions.
- **Testing Notes:** **Light gate** for plugin suite, plus targeted **Strict** contract validation in core loader.

### Story POST-01.3 — Plugin command discoverability parity
- **As an** operator, **I want** plugin commands to appear in standard help/introspection output, **so that** extension features remain discoverable.
- **Traceability:** `FR-008`, `FR-009`
- **Acceptance Criteria:**
  - Plugin commands are listed in help and introspection outputs with examples.
  - Plugin command validation follows same error schema as core commands.
  - Uninstalling/disabling plugin removes commands cleanly at startup boundary.
- **Testing Notes:** **Light gate** for plugin UX behavior.

## EPIC-POST-02: Advanced Orchestration and Extension Tracks
**Goal:** Add optional advanced patterns without changing deterministic default runtime.
**Primary FR coverage:** `FR-003`, `FR-008`
**Key ADR constraints:** `ADR-003`, `ADR-004`, `ADR-012`

### Story POST-02.1 — Optional graph adapter for advanced chains
- **As a** workflow engineer, **I want** graph-based execution as an optional adapter, **so that** complex branching can be introduced without replacing core orchestration.
- **Traceability:** `FR-003`, `FR-008`
- **Acceptance Criteria:**
  - Graph adapter is optional and disabled by default.
  - Deterministic core remains default execution path.
  - Adapter invocation emits same observability schema and respects policy controls.
- **Testing Notes:** **Light gate** (experimental adapter) with interface conformance checks.

### Story POST-02.2 — Multi-agent review chain template
- **As a** team lead, **I want** reusable generator/reviewer/corrector/validator templates, **so that** quality can improve for selected workflows.
- **Traceability:** `FR-003`
- **Acceptance Criteria:**
  - Template defines bounded loop limits and role handoff schema.
  - Role chain execution remains policy-gated for tool usage.
  - Final output includes role-attributed decision trace.
- **Testing Notes:** **Light gate** (advanced orchestration) + targeted policy enforcement checks.

## 5) Story-to-FR Traceability Matrix
| Story ID | FR Coverage |
|---|---|
| MVP-00.1 | FR-002, FR-007 |
| MVP-01.1 | FR-001, FR-009 |
| MVP-01.2 | FR-002 |
| MVP-01.3 | FR-003 |
| MVP-01.4 | FR-006 |
| MVP-01.5 | FR-004 |
| MVP-02.1 | FR-005, FR-010 |
| MVP-02.2 | FR-005, FR-010 |
| MVP-02.3 | FR-005, FR-010 |
| MVP-02.4 | FR-005 |
| MVP-03.1 | FR-007, FR-002 |
| MVP-03.2 | FR-007 |
| MVP-03.3 | FR-007 |
| MVP-03.4 | FR-007 |
| MVP-04.1 | FR-004 |
| MVP-04.2 | FR-003, FR-004 |
| MVP-05.1 | FR-009 |
| MVP-05.2 | FR-009, FR-001 |
| MVP-05.3 | FR-010, FR-005 |
| POST-01.1 | FR-008 |
| POST-01.2 | FR-008 |
| POST-01.3 | FR-008, FR-009 |
| POST-02.1 | FR-003, FR-008 |
| POST-02.2 | FR-003 |

## 6) Prioritized Backlog Order (Global)
1. `MVP-00.1`
2. `MVP-01.1`
3. `MVP-01.2`
4. `MVP-01.5`
5. `MVP-02.1`
6. `MVP-02.2`
7. `MVP-03.2`
8. `MVP-03.1`
9. `MVP-01.4`
10. `MVP-01.3`
11. `MVP-03.4`
12. `MVP-04.1`
13. `MVP-04.2`
14. `MVP-02.4`
15. `MVP-02.3`
16. `MVP-05.2`
17. `MVP-05.1`
18. `MVP-05.3`
19. `MVP-03.3`
20. `POST-01.1`
21. `POST-01.2`
22. `POST-01.3`
23. `POST-02.1`
24. `POST-02.2`

## 7) Suggested Sprint Slicing
Assumption: 2-week sprints, 5-7 stories per sprint depending on complexity.

### Sprint 1 (MVP Foundation)
- `MVP-00.1`, `MVP-01.1`, `MVP-01.2`, `MVP-01.5`, `MVP-02.1`, `MVP-03.2`
- Exit: repository scaffold + CI quality baseline + deterministic command/chat routing + lifecycle + tool contract baseline + baseline security checks + baseline correlated logging.

### Sprint 2 (MVP Safety Core)
- `MVP-02.2`, `MVP-01.4`, `MVP-03.1`, `MVP-02.4`
- Exit: confirmation gates, safe context handling, persistent execution history, backend policy resolver.

### Sprint 3 (MVP Intelligence + Providers)
- `MVP-01.3`, `MVP-03.4`, `MVP-04.1`, `MVP-04.2`, `MVP-02.3`
- Exit: bounded conversational loop, extended agent/tool correlation, provider contracts/adapters, explicit `--approve-plan` mode.

### Sprint 4 (MVP Operator Experience + Hardening)
- `MVP-05.2`, `MVP-05.1`, `MVP-05.3`, `MVP-03.3`
- Exit: terminal UX/discoverability complete, retention policy active, MVP readiness review.

### Sprint 5 (Post-MVP Plugin Enablement)
- `POST-01.1`, `POST-01.2`, `POST-01.3`
- Exit: plugin discovery, compatibility checks, and discoverability parity delivered.

### Sprint 6 (Post-MVP Advanced Extensions)
- `POST-02.1`, `POST-02.2`
- Exit: optional graph adapter and multi-agent review template available as controlled extensions.

## 8) CI and Test-Gate Application Summary
- **Strict gate stories (core/runtime/security/persistence/provider contracts):** all `MVP-*` stories, including `MVP-05.2` (command contract UX) and `MVP-05.3` (safety confirmation UX), except adapter-specific checks in `MVP-04.2` and presentation-focused UX checks in `MVP-05.1`.
- **Moderate gate stories (provider adapters + presentation UX):** adapter implementation portion of `MVP-04.2` and presentation/readability checks in `MVP-05.1`.
- **Light gate stories (plugins/experimental adapters):** all `POST-*` stories, with strict checks retained at core contract boundaries.

## 9) Notes for Story Authoring Next Step
- This backlog is implementation-ready for decomposition into one-story-per-file execution artifacts.
- Recommended follow-up workflow: `bmad-create-story` in prioritized order starting at `MVP-00.1`.
