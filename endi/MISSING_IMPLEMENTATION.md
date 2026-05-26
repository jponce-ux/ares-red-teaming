# ENDI Missing or Unfinished Implementation

This analysis is scoped to the Python `endi/` subproject only. The root ARES
project is Rust-based; ENDI is treated here as a separate imported Python CLI
assistant project.

Source artifacts reviewed:

- `endi/_bmad-output/planning-artifacts/endi-prd.md`
- `endi/_bmad-output/planning-artifacts/endi-architecture-final.md`
- `endi/_bmad-output/planning-artifacts/endi-epics-stories-backlog.md`
- `endi/_bmad-output/implementation-artifacts/sprint-status.yaml`
- `endi/_bmad-output/implementation-artifacts/stories/`
- `endi/src/endi/`

## Summary

BMAD marks all MVP epics through `epic-mvp-05` as done, but several areas are
implemented as contracts, metadata, scaffolding, or placeholder behavior rather
than runnable product functionality.

The most important gap is that ENDI currently routes free-text input to a
placeholder conversation handler. It does not yet call OpenAI, Anthropic,
Ollama, or any other real model provider.

## Missing or Unfinished Items

| ID | Area | Status | BMAD Reference | Current Implementation | Missing Work |
|----|------|--------|----------------|------------------------|--------------|
| M001 | Real AI chat path | Not implemented | `FR-001`, `FR-003`, MVP-01.3 | `cli.py` routes free text to `_handle_conversation()`, which echoes `[conversation] {text}`. | Replace placeholder handler with provider-backed chat generation. |
| M002 | Provider adapters | Not implemented | MVP-04.2, architecture provider set OpenAI/Anthropic/Ollama | `providers.py` defines contracts, defaults, registry validation, and fallback policy. | Implement concrete OpenAI, Anthropic, and Ollama adapters plus config/credential loading. |
| M003 | Conversational tool orchestration | Partially implemented | `FR-003`, MVP-01.3 | `conversation.py` has a bounded loop; `routing.py` default runtime immediately completes. | Add real action selection, tool-call decisioning, tool execution, observations, and provider-backed synthesis. |
| M004 | Filesystem tools | Not implemented | PRD MVP must-have: filesystem tool category; `FR-004`, `FR-005` | Tool registry contract exists, but no filesystem tool contracts or handlers are registered. | Add filesystem read/write tools with schema validation, capability checks, redaction, and confirmation rules. |
| M005 | Shell execution tools | Not implemented | PRD MVP must-have: shell tool category; `FR-004`, `FR-005` | Backend mapping includes `shell.exec`, but there is no shell tool implementation. | Add shell execution tool with safe input contract, capability gating, confirmation, timeout, and audit trail. |
| M006 | Real command workflows | Partially implemented | `FR-002`, `FR-009`, MVP-01.2, MVP-05.2 | Workflow lifecycle exists, but CLI command execution returns placeholder strings for most commands. | Implement actual workflows for advertised commands or remove placeholder commands from discoverability. |
| M007 | Interactive shell mode | Not implemented | Architecture CLI layer: `endi` then `/command` | CLI exposes `version` and `submit`; no persistent interactive shell loop exists. | Add root interactive shell or `endi shell` using Prompt Toolkit. |
| M008 | `--approve-plan` CLI surface | Partially implemented | MVP-02.3, architecture confirmation policy | Routing supports approve-plan context internally. | Add Typer flags/options for `--approve-plan`, `--non-interactive`, plan artifact input, and context wiring. |
| M009 | Worker/container/remote execution | Interface only | MVP-02.4, architecture execution backends | `LocalBackend` is concrete; worker/container/remote are protocol/interface markers. | Implement worker backend at minimum if sensitive capabilities map to `worker` by default. |
| M010 | Sandbox enforcement | Not implemented | Architecture sandboxing section | Backend selection models isolation levels, but no sandbox policy enforcement exists. | Add sandbox profile policy and execution path for high-risk tools/chains. |
| M011 | JSON log sink | Partially implemented | `FR-007`, MVP-03.2 | Telemetry payloads and SQLite history exist. | Emit structured JSON logs through a runtime logging/tracing sink. |
| M012 | Tool-call telemetry from real tools | Partially implemented | `FR-007`, MVP-03.4 | Correlation structures exist, but there are no real registered tool calls from CLI chat. | Wire real tool invocation events into telemetry and persistence. |
| M013 | CLI JSON output mode | Not implemented | PRD should-have structured output modes | CLI renders Rich panels only. | Add `--output json` or equivalent machine-readable output for chaining. |
| M014 | Plugin loader | Not implemented | `FR-008`, POST-01.1 | Plugin stories remain backlog; no loader exists. | Implement local manifest discovery and package entry point discovery. |
| M015 | Plugin compatibility/version checks | Not implemented | POST-01.2 | No plugin runtime exists. | Add SemVer/capability compatibility checks at plugin load time. |
| M016 | Plugin command discoverability | Not implemented | POST-01.3 | Help/introspection reads only the static core command catalog. | Include loaded plugin commands in help/introspection once plugin loading exists. |
| M017 | Optional graph adapter | Not implemented | POST-02.1 | No graph adapter implementation exists. | Add optional adapter while keeping deterministic workflow as default. |
| M018 | Multi-agent review chain template | Not implemented | POST-02.2 | No multi-agent template implementation exists. | Add generator/reviewer/corrector/validator template with bounded role handoff. |
| M019 | KPI/benchmark validation | Not implemented | PRD KPI-1 through KPI-6 | Tests validate contracts, but no benchmark or KPI measurement harness exists. | Add benchmark/load tests for routing reliability, workflow success rate, and nominal-load behavior if KPIs are still active. |
| M020 | Real provider fallback execution | Partially implemented | MVP-04.2 | Explicit-only fallback decision policy exists. | Invoke Ollama/local fallback only when explicitly enabled and a real provider call fails for allowed reasons. |

## High-Priority Implementation Order

1. Implement real provider adapters and configuration.
2. Replace placeholder free-text conversation with provider-backed chat.
3. Add filesystem and shell tools with capability/confirmation controls.
4. Wire tool execution into the bounded conversation loop.
5. Add CLI flags for approve-plan, non-interactive execution, and JSON output.
6. Implement worker/sandbox execution for high-risk tools or adjust capability
   backend defaults until worker execution exists.
7. Add structured JSON logging in addition to SQLite history.

## Notes

- The current code has substantial contract and safety scaffolding. The gaps
  are mostly in runnable adapters, real commands, real tools, and user-facing
  CLI integration.
- Post-MVP plugin and graph/multi-agent stories are correctly still backlog in
  `sprint-status.yaml`; they are included here because they are explicitly
  planned but not implemented.
- This file does not evaluate the Rust ARES project. It only tracks unfinished
  work in the Python ENDI subproject.
