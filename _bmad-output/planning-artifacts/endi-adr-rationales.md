# ENDI ADR Decision Rationales (Workshop Record)

This document captures the rationale provided during the interactive architecture decision workshop.
It is intentionally separate from the final architecture document.

## ADR-001 — Language/Runtime
**Decision:** Python

**Rationale captured:**
- Python selected as the primary runtime for ENDI v1.
- No extended rationale was provided at decision time beyond direct selection.

---

## ADR-002 — CLI Framework
**Decision:** `Typer + Rich + Prompt Toolkit`

**Rationale captured:**
- Best fit for critical ENDI CLI needs: command-style agent flows, autocompletion, rich terminal UX, modularity, and long-term maintainability.
- `Typer` provides clean syntax, type-hint-native command definitions, and automatic help.
- `Rich` supports high-quality tables/panels/log/progress UI.
- `Prompt Toolkit` enables REPL-style interaction (autocomplete, multiline input, shell UX).
- Supports dual interface model:
  - direct CLI commands (`endi deploy ...`)
  - interactive shell (`endi` then `/command ...`).

---

## ADR-003 — Workflow Orchestration Approach
**Decision:** Hybrid — in-house deterministic workflow core + optional graph adapter

**Rationale captured:**
- ENDI orchestrates two different workloads:
  - deterministic operational workflows
  - agent reasoning loops.
- Deterministic workflows need strict ordering, retries, reproducibility, and auditability.
- Graph runtime is useful for advanced branching/multi-agent reasoning, but overkill as global default.
- Avoids framework lock-in while preserving future advanced chains.
- Key rule: workflows orchestrate agents; graphs are optional execution paths, not the global runtime.

---

## ADR-004 — Agent Runtime Boundaries
**Decision:** Hybrid — in-process by default + optional isolated worker mode

**Rationale captured:**
- In-process default preserves interactive CLI performance and dev velocity.
- Optional worker isolation supports high-risk chains (shell/filesystem mutation/network-sensitive operations).
- Supports capability-driven isolation policy (agent/tool metadata can request worker mode).
- Enables future isolation backends (subprocess, container, k8s job, remote service) without redesign.

---

## ADR-005 — Plugin Architecture and Packaging
**Decision:** Hybrid — local manifest plugins for MVP + package plugins for long-term distribution

**Rationale captured:**
- Local plugins optimize MVP iteration speed and low-friction internal development.
- Package-based plugins (`entry_points`) support long-term ecosystem scale and governance.
- Single plugin interface/registry model across both discovery channels.
- Dual discovery model:
  - local filesystem plugins (`~/.endi/plugins`)
  - installed package plugins (`importlib.metadata.entry_points(group="endi.plugins")`).
- Preserves extensibility while avoiding temporary architecture dead-ends.

---

## ADR-006 — Permission Model and Sandboxing
**Decision:** Hybrid — capability classes + confirmation gates by default + sandbox profiles for high-risk tools/chains

**Rationale captured:**
- Safety needs three independent controls:
  - capability authorization
  - user confirmation gates
  - constrained execution environments.
- Safe-by-default UX principle:
  - reads: seamless
  - writes: confirmed
  - dangerous operations: sandboxed.
- Aligns with previous hybrid execution decisions and scales to future policy/RBAC layers.

---

## ADR-007 — Context and State Storage
**Decision:** Hybrid — ephemeral runtime context + durable structured local persistence for execution history

**Rationale captured:**
- Runtime state and historical trace data are different classes of data and should not share storage model.
- In-memory runtime context keeps agent loop fast and low-friction.
- SQLite persistence provides auditable and queryable command/workflow/tool history.
- Large artifacts should remain on disk with DB path references.
- Enables replay, debugging, and operational introspection without bloating runtime memory model.

---

## ADR-008 — Provider Abstraction Strategy
**Decision:** Capability-split interfaces with adapter composition (`ChatProvider`, `EmbeddingProvider`, `ToolCallingProvider`)

**Rationale captured:**
- Avoids lowest-common-denominator generic provider abstraction.
- Models what agents need (capabilities), not vendor names.
- Supports multi-provider routing and local provider partial-capability scenarios.
- Keeps agents provider-agnostic and vendor adapters isolated.
- Future capability expansion remains additive (vision/speech/retrieval/etc.).

---

## ADR-009 — Initial Provider Lineup
**Decision:** OpenAI + Anthropic + Ollama (dual-cloud + local fallback)

**Rationale captured:**
- Balances tool-calling reliability, reasoning quality, embeddings support, and local/offline operation.
- OpenAI: strong general chat/embeddings ecosystem.
- Anthropic: strong reasoning and tool-loop reliability.
- Ollama: local privacy/offline fallback and experimentation.
- Maximizes provider-independence and practical adoption paths.

---

## ADR-010 — Observability Baseline
**Decision:** Hybrid — structured JSON logs + correlation IDs baseline + optional OpenTelemetry interface/exporter

**Rationale captured:**
- Immediate local debugging value without requiring production telemetry backend on day one.
- Correlation hierarchy enables trace-like reconstruction:
  `session -> command -> workflow -> step -> agent -> tool_call`.
- OTel-ready abstraction enables future enterprise-grade observability without runtime redesign.

---

## ADR-011 — Testing Strategy and CI Quality Gates
**Decision:** Hybrid quality gates (strict core, moderate adapters, lighter plugins/experiments)

**Rationale captured:**
- Core platform failures are high risk; extension surfaces need iteration speed.
- Strict gates for runtime/security/permission/persistence/contract-critical modules.
- Lighter gates for plugins and experiments to preserve ecosystem velocity.
- Balances safety and contributor experience.

---

## ADR-012 — Runtime/Deployment Topology
**Decision:** Hybrid — local-first runtime + pluggable execution backends behind unified interface

**Rationale captured:**
- Maintain simple CLI-first operator experience for v1.
- Keep future-ready path for worker/container/remote execution without architecture rewrite.
- Runtime remains backend-agnostic; backend selection can be policy-driven.
- MVP can ship with `LocalBackend` while preserving extensibility contracts.

---

## ADR-013 — Versioning and Compatibility Policy
**Decision:** Hybrid — strict SemVer for core runtime contracts + capability-version contracts for plugins/providers + deprecation windows + load-time compatibility checks

**Rationale captured:**
- ENDI has two stability layers:
  - core platform contracts (must be highly stable)
  - extension capabilities (must evolve independently).
- SemVer alone is too coarse for extension compatibility.
- Best-effort compatibility is too weak for platform reliability.
- Capability contracts + load-time validation prevent silent breakage and improve upgrade predictability.

---

## ADR-014 — Workshop Continuation Decision
**Decision:** Continue to lock v1 default configuration profile before final architecture generation

**Rationale captured:**
- Reduce implementation ambiguity before epics/stories decomposition.
- Produce explicit operational defaults, not placeholders.

---

## ADR-015 — Default Provider Routing
**Decision:**
- `chat = openai:gpt-4o-mini`
- `tools = anthropic:claude-3.7-sonnet`
- `embeddings = openai:text-embedding-3-large`
- `local_fallback = ollama`

**Rationale captured:**
- Capability-specific optimization:
  - fast/reliable chat path
  - strong tool-loop reasoning
  - stable embeddings
  - local/offline fallback path.
- Preserves simple defaults while leveraging provider strengths.

---

## ADR-016 — Local Fallback Behavior
**Decision:** Explicit-only local fallback (`ollama`) — no automatic fallback by default

**Rationale captured:**
- Silent fallback changes behavior quality and can compromise deterministic automation.
- Prevents hidden mixed-provider execution within a run.
- Keeps user in control and preserves auditable execution consistency.
- Optional explicit opt-in remains available via CLI/config flags.

---

## ADR-017 — Default Execution Backend Policy
**Decision:** Local default + explicit capability-to-backend mapping table

**Rationale captured:**
- Explicit policy is safer than implicit heuristics in a plugin ecosystem.
- Runtime-owned capability routing is auditable and configurable.
- Recommended default mapping:
  - `repo.read -> local`, `repo.write -> worker`
  - `filesystem.read -> local`, `filesystem.write -> worker`
  - `network.outbound -> local`, `network.admin -> worker`
  - `shell.exec -> worker`
  - `system.modify -> worker`
  - `cloud.read -> local`, `cloud.write -> worker`
- Resolution rule: highest isolation requirement wins.

---

## ADR-018 — Confirmation Gate Policy
**Decision:** Hybrid — per-action confirmation by default + explicit `--approve-plan` mode

**Rationale captured:**
- Default per-action confirmation preserves safety for sensitive operations.
- `--approve-plan` supports low-friction trusted automation and CI.
- Ensures users approve real planned actions, not opaque blanket intent.
- Aligns safety-by-default with operational usability.

---

## ADR-019 — Local Retention Defaults
**Decision:** Keep 30 days or 2 GB total (whichever comes first), auto-prune oldest

**Rationale captured:**
- Bounded default protects developer machines from silent disk growth.
- 30-day history is usually sufficient for debugging and regression analysis.
- Retention algorithm:
  1. prune by age
  2. then prune oldest by size threshold until under limit.
- Supports zero-maintenance local operation with optional manual storage commands.

---

## Consolidated Default Profile (Locked in Workshop)

```yaml
providers:
  chat:
    default: openai:gpt-4o-mini
  tools:
    default: anthropic:claude-3.7-sonnet
  embeddings:
    default: openai:text-embedding-3-large
  local_fallback:
    provider: ollama
    mode: explicit_only

runtime:
  default_backend: local
  capability_backends:
    repo.read: local
    repo.write: worker
    filesystem.read: local
    filesystem.write: worker
    network.outbound: local
    network.admin: worker
    shell.exec: worker
    system.modify: worker
    cloud.read: local
    cloud.write: worker

confirmations:
  mode: per_action
  sensitive_capabilities:
    - repo.write
    - filesystem.write
    - shell.exec
    - cloud.write
    - system.modify
    - network.admin
  approve_plan_mode: true

storage:
  history_days: 30
  max_storage_gb: 2
  auto_prune: true
```
