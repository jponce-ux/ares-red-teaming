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
| M001 | Real AI chat path | Completed in `001-endi-runtime-completion` | `FR-001`, `FR-003`, MVP-01.3 | `cli.py` now builds a chat provider from runtime context and routes free text through provider-backed generation. | Continue hardening provider UX and real credential docs. |
| M002 | Provider adapters | Completed in `001-endi-runtime-completion` | MVP-04.2, architecture provider set OpenAI/Anthropic/Ollama | `providers.py` now includes OpenAI-compatible, Anthropic-compatible, and Ollama chat adapters. | Add streaming and richer provider-specific error mapping later if needed. |
| M003 | Conversational tool orchestration | Partially implemented | `FR-003`, MVP-01.3 | `conversation.py` has a bounded loop; `routing.py` default runtime immediately completes. | Add real action selection, tool-call decisioning, tool execution, observations, and provider-backed synthesis. |
| M004 | Filesystem tools | Completed in `001-endi-runtime-completion` | PRD MVP must-have: filesystem tool category; `FR-004`, `FR-005` | `builtin_tools.py` registers filesystem read/write tools through `ToolRegistry`. | Integrate tool invocation into richer conversational planning later. |
| M005 | Shell execution tools | Completed in `001-endi-runtime-completion` | PRD MVP must-have: shell tool category; `FR-004`, `FR-005` | `builtin_tools.py` registers `shell.exec` with timeout and structured stdout/stderr/exit-code payload. | Add stronger shell policy/sandbox integration later. |
| M006 | Real command workflows | Partially implemented | `FR-002`, `FR-009`, MVP-01.2, MVP-05.2 | Workflow lifecycle exists, but CLI command execution returns placeholder strings for most commands. | Implement actual workflows for advertised commands or remove placeholder commands from discoverability. |
| M007 | Interactive shell mode | Completed in `001-endi-runtime-completion` | Architecture CLI layer: `endi` then `/command` | CLI now exposes `endi shell` with `/exit` and `/quit`. | Add richer shell session state later. |
| M008 | `--approve-plan` CLI surface | Partially completed in `001-endi-runtime-completion` | MVP-02.3, architecture confirmation policy | CLI now exposes `--approve-plan` and `--non-interactive` context flags. | Add plan artifact file input for full approve-plan automation. |
| M009 | Worker/container/remote execution | Interface only | MVP-02.4, architecture execution backends | `LocalBackend` is concrete; worker/container/remote are protocol/interface markers. | Implement worker backend at minimum if sensitive capabilities map to `worker` by default. |
| M010 | Sandbox enforcement | Not implemented | Architecture sandboxing section | Backend selection models isolation levels, but no sandbox policy enforcement exists. | Add sandbox profile policy and execution path for high-risk tools/chains. |
| M011 | JSON log sink | Completed in `001-endi-runtime-completion` | `FR-007`, MVP-03.2 | `runtime_logging.py` writes sanitized JSON Lines events when `--log-json` is configured. | Expand event coverage if needed. |
| M012 | Tool-call telemetry from real tools | Partially implemented | `FR-007`, MVP-03.4 | Correlation structures exist, but there are no real registered tool calls from CLI chat. | Wire real tool invocation events into telemetry and persistence. |
| M013 | CLI JSON output mode | Completed in `001-endi-runtime-completion` | PRD should-have structured output modes | `endi submit --output json` now emits a machine-readable envelope. | Add schema documentation later. |
| M014 | Plugin loader | Partially completed in `001-endi-runtime-completion` | `FR-008`, POST-01.1 | `plugins.py` now loads local JSON manifests for command metadata only. | Package entry point discovery and executable plugin runtime remain backlog. |
| M015 | Plugin compatibility/version checks | Not implemented | POST-01.2 | No plugin runtime exists. | Add SemVer/capability compatibility checks at plugin load time. |
| M016 | Plugin command discoverability | Partially completed in `001-endi-runtime-completion` | POST-01.3 | `--plugin-dir` command metadata appears in help/introspection. | Dynamic startup plugin registry remains backlog. |
| M017 | Optional graph adapter | Not implemented | POST-02.1 | No graph adapter implementation exists. | Add optional adapter while keeping deterministic workflow as default. |
| M018 | Multi-agent review chain template | Not implemented | POST-02.2 | No multi-agent template implementation exists. | Add generator/reviewer/corrector/validator template with bounded role handoff. |
| M019 | KPI/benchmark validation | Not implemented | PRD KPI-1 through KPI-6 | Tests validate contracts, but no benchmark or KPI measurement harness exists. | Add benchmark/load tests for routing reliability, workflow success rate, and nominal-load behavior if KPIs are still active. |
| M020 | Real provider fallback execution | Completed in `001-endi-runtime-completion` | MVP-04.2 | Provider-backed chat now attempts Ollama fallback only when explicit fallback policy allows it. | Add integration tests against a live local Ollama instance later. |

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
