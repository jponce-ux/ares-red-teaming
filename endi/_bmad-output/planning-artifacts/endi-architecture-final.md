# ENDI Finalized Architecture (v1)

## 1. Document Status
- **Project:** ENDI (Enhanced Natural-language Directed Intelligence)
- **Status:** Finalized architecture baseline for implementation planning
- **Purpose:** Convert the approved ADR decisions into an implementation-ready architecture specification prior to epics/stories generation
- **Source Inputs:**
  - `docs/terminal_ai_assistant_architecture.md`
  - `_bmad-output/planning-artifacts/endi-prd.md`
  - `_bmad-output/planning-artifacts/endi-adr-rationales.md`

---

## 2. Architecture Principles (Locked)
1. **Human-in-the-loop**: users remain in control of sensitive and destructive actions.
2. **Modularity**: commands, workflows, agents, tools, providers, and plugins evolve independently.
3. **Safety-by-default**: capability gating, confirmation controls, and sandbox escalation for risky operations.
4. **Provider-independence**: capability-based interfaces and adapter composition instead of vendor lock-in.
5. **Deterministic operations where possible**: workflow orchestration remains explicit and state-driven.
6. **Observability-first runtime**: structured execution traces with correlation IDs across all layers.

---

## 3. Locked Decision Summary (ADR-001 to ADR-019)

| ADR | Topic | Final Decision |
|---|---|---|
| ADR-001 | Language/runtime | Python |
| ADR-002 | CLI stack | Typer + Rich + Prompt Toolkit |
| ADR-003 | Orchestration | Hybrid: deterministic core + optional graph adapter |
| ADR-004 | Agent boundaries | Hybrid: in-process default + optional worker isolation |
| ADR-005 | Plugin packaging | Hybrid: local manifests + package entry points |
| ADR-006 | Permissions/sandbox | Hybrid: capabilities + confirmations + selective sandbox |
| ADR-007 | Context/state storage | Hybrid: in-memory runtime + durable local execution history |
| ADR-008 | Provider abstraction | Capability-split interfaces + adapter composition |
| ADR-009 | Initial providers | OpenAI + Anthropic + Ollama |
| ADR-010 | Observability | JSON logs + correlation IDs + optional OTel |
| ADR-011 | Testing/CI | Hybrid strict-core + lighter-extension gates |
| ADR-012 | Runtime topology | Local-first + pluggable execution backends |
| ADR-013 | Versioning/compatibility | Core SemVer + capability contracts + load-time checks |
| ADR-014 | Workshop continuation | Lock default config before finalization |
| ADR-015 | Provider defaults | chat=openai, tools=anthropic, embeddings=openai, local=ollama |
| ADR-016 | Local fallback policy | Explicit-only (no silent auto fallback) |
| ADR-017 | Backend mapping policy | Explicit capability->backend mapping table |
| ADR-018 | Confirmation policy | Per-action default + optional `--approve-plan` |
| ADR-019 | Retention policy | 30 days or 2 GB, auto-prune oldest |

---

## 4. System Architecture Overview

```text
Terminal User
   |
   v
CLI Layer (Typer + Prompt Toolkit + Rich)
   |
   v
Command Router / Input Classifier
   |------------------------------|
   |                              |
   v                              v
Deterministic Workflow Engine   Conversational Agent Path
   |                              |
   |-------> Agent Runtime <------|
                |
                v
         Execution Runtime
      (backend selector + policy)
                |
   |------------|------------|------------|
   v            v            v            v
LocalBackend  WorkerBackend  ContainerBackend*  RemoteBackend*
                               (*interface in v1)
                |
                v
Tool Layer -> Provider Adapters -> External Systems

Cross-cutting: Permissions, Confirmations, Observability, Context, Persistence
```

### 4.1 Key Separation Rules
- Workflows orchestrate steps and remain deterministic.
- Agent loops are bounded and policy-controlled.
- Graph execution is optional and adapter-based (not the default orchestration model).
- Runtime selects execution backend from explicit capability policy.

---

## 5. Runtime Components

## 5.1 CLI Layer
- Primary framework: `Typer`
- Interactive shell support: `Prompt Toolkit`
- Rendering and UX: `Rich`
- Supported interaction styles:
  - Direct command mode (`endi deploy service-x`)
  - Interactive shell mode (`endi` then `/deploy service-x`)

## 5.2 Command Routing
- Inputs prefixed with `/` route to deterministic workflow commands.
- Free-text requests route to conversational agent path.
- Validation errors are structured and non-executing.

## 5.3 Workflow Engine (Deterministic Core)
Lifecycle:
1. initialize
2. validate
3. plan (optional)
4. execute
5. collect
6. output
7. finalize

Core guarantees:
- deterministic step sequencing
- explicit failure states
- traceable step-level telemetry

## 5.4 Agent Runtime
- Bounded agent loop with iteration limits.
- Controlled tool access via capability checks.
- Execution boundary selected per policy (`inprocess` default, `worker` as needed).
- Supports optional multi-agent patterns (generator/reviewer/corrector/validator).

## 5.5 Execution Backends
- **Implemented in v1:** `LocalBackend`
- **Defined interfaces for future use:** `WorkerBackend`, `ContainerBackend`, `RemoteBackend`
- Backend selection rule: capability-to-backend mapping, with highest isolation requirement winning.

---

## 6. Plugin and Registry Architecture

## 6.1 Unified Plugin Contract
All plugin sources implement the same registration contract for:
- commands
- workflows
- agents
- tools

## 6.2 Discovery Sources
1. Local manifest plugins (`~/.endi/plugins/...`)
2. Installed package plugins (`entry_points(group="endi.plugins")`)

## 6.3 Registry Boundaries
- Core runtime exposes registries and validation hooks.
- Plugins extend capabilities through registration only (no direct core mutation).

---

## 7. Permission, Confirmation, and Sandboxing

## 7.1 Capability Model
Baseline capabilities include:
- `repo.read`, `repo.write`
- `filesystem.read`, `filesystem.write`
- `shell.exec`
- `network.outbound`, `network.admin`
- `cloud.read`, `cloud.write`
- `system.modify`

## 7.2 Confirmation Policy
Default mode:
- per-action confirmation for sensitive capabilities:
  - `repo.write`
  - `filesystem.write`
  - `shell.exec`
  - `cloud.write`
  - `system.modify`
  - `network.admin`

Optional mode:
- `--approve-plan` to confirm planned sensitive actions once up front
- compatible with non-interactive automation (`--approve-plan --non-interactive`)

## 7.3 Sandboxing
- High-risk tools/chains can require sandbox profile enforcement.
- Sandbox execution path integrates with worker/container backends.

---

## 8. Context and Persistence Model

## 8.1 Runtime Context (Ephemeral)
In-memory only:
- session context
- workflow temporary state
- agent scratch state
- intermediate artifacts metadata

## 8.2 Durable Execution History (Local)
Structured local persistence (SQLite) for:
- sessions
- commands
- workflows
- steps
- tool calls
- outcomes and timing metadata

## 8.3 Artifact Storage
- Large artifacts stored on filesystem under local data directory.
- DB stores references/paths, not large blobs.

---

## 9. Provider Architecture

## 9.1 Capability Interfaces
- `ChatProvider`
- `EmbeddingProvider`
- `ToolCallingProvider`

## 9.2 Initial Provider Set
- OpenAI
- Anthropic
- Ollama

## 9.3 Default Routing (v1)
- chat: `openai:gpt-4o-mini`
- tools: `anthropic:claude-3.7-sonnet`
- embeddings: `openai:text-embedding-3-large`
- local fallback provider: `ollama` (explicit-only policy)

## 9.4 Fallback Policy
- No automatic silent fallback by default.
- Local provider use must be explicitly requested by user/config.

---

## 10. Observability Architecture

## 10.1 Baseline
- Structured JSON logs
- Correlation IDs across execution chain

Correlation hierarchy:
- `session_id -> command_id -> workflow_id -> step_id -> agent_id -> tool_call_id`

## 10.2 Trace-Ready Abstraction
- OTel-compatible tracing interface included in architecture.
- No-op/default tracer allowed in MVP.
- Optional exporter integration path for future telemetry backends.

---

## 11. Testing and CI Quality Model

## 11.1 Tiered Quality Gates
- **Strict gates:** core runtime/security/permissions/persistence/provider contracts
- **Moderate gates:** provider adapters
- **Light gates:** plugins and experiments

## 11.2 Suggested MVP Tooling
- `pytest`, `pytest-cov`
- `ruff`
- `mypy`
- optional security/dependency checks

## 11.3 Required Test Focus Areas
- permission enforcement and confirmation behavior
- backend selection and isolation policy
- deterministic workflow execution lifecycle
- provider capability contracts
- correlation/event continuity

---

## 12. Runtime Topology and Deployment

## 12.1 v1 Deployment Mode
- Local-first CLI runtime, single-machine operation by default.

## 12.2 Expansion Modes (post-v1)
- local worker execution
- containerized sandbox execution
- remote/distributed execution service

All expansion modes reuse the same runtime interface contract.

---

## 13. Versioning and Compatibility

## 13.1 Core Versioning
- Strict SemVer for core/runtime contracts.

## 13.2 Capability Versioning
- Versioned capability contracts for plugins/providers.
- Load-time compatibility checks enforce hard-fail for incompatible extensions.

## 13.3 Deprecation Policy
- Introduce capability replacements before removal.
- Emit deprecation warnings with removal target version.
- Remove deprecated contracts on major version boundaries.

---

## 14. Locked v1 Default Configuration Profile

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

Retention behavior:
1. prune by age (`history_days`)
2. if still over size budget, prune oldest until under `max_storage_gb`

---

## 15. Implementation Readiness Notes for Epics/Stories

This architecture is ready for decomposition into epics/stories with these immediate implementation tracks:
1. Core runtime skeleton (CLI/router/workflow engine/agent loop)
2. Security and policy layer (capabilities/confirmations/backend resolver)
3. Persistence and observability baseline (SQLite + JSON event logs)
4. Provider capability interfaces and initial adapters
5. Plugin loader/registries (local + package discovery)
6. Tiered CI/testing gates by component class

---

## 16. Out-of-Scope for v1 Baseline
- Mandatory distributed runtime deployment
- Full OTel backend setup by default
- Fully autonomous destructive actions
- Global always-on automatic provider fallback

---

## 17. Final Architecture Outcome
ENDI v1 architecture is finalized as a **hybrid, policy-driven, provider-independent terminal AI platform** with:
- deterministic operational core
- bounded agent reasoning
- explicit safety controls
- modular extension model
- local-first execution with future-ready backend abstraction

This architecture is approved as the baseline input to `bmad-create-epics-and-stories`.
