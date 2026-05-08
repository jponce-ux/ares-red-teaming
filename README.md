# ENDI

Enhanced Natural-language Directed Intelligence (**ENDI**) is a workflow-oriented, terminal-native AI assistant designed for development and operations work.

It combines deterministic command workflows with bounded conversational reasoning so teams can move faster without giving up safety, control, or traceability.

## Current Status

This repository is currently in **planning-complete / implementation-start** phase.

- Core architecture is finalized
- PRD and epics/stories are defined
- Sprint tracking artifacts are in place
- MVP implementation is in progress.

## What ENDI Aims to Deliver

- Hybrid interaction model: `/command` workflows + natural language requests
- Deterministic workflow engine for operational reliability
- Bounded agent loops with controlled tool usage
- Safety-by-default execution (permissions + confirmations)
- Provider-independent architecture (multi-provider support)
- Strong observability and auditability (structured logs + correlation IDs)
- Extensible plugin model for commands/workflows/tools/agents

## Architecture Snapshot (v1)

- **Language/runtime:** Python
- **CLI stack:** Typer + Rich + Prompt Toolkit
- **Orchestration:** deterministic core + optional graph adapter
- **Execution model:** local-first runtime with pluggable backends
- **Providers:** OpenAI + Anthropic + Ollama (explicit local fallback)
- **Storage model:** in-memory runtime context + durable local execution history
- **Security model:** capability-based permissions + confirmation gates + sandbox path for risky operations

For full details, see:

- `docs/terminal_ai_assistant_architecture.md`
- `docs/runtime-error-envelope-parity.md`
- `_bmad-output/planning-artifacts/endi-prd.md`
- `_bmad-output/planning-artifacts/endi-architecture-final.md`
- `_bmad-output/planning-artifacts/endi-adr-rationales.md`

## Repository Map

- `docs/` — source architecture and design documentation
- `_bmad-output/planning-artifacts/` — PRD, ADR rationale, final architecture, backlog planning docs
- `_bmad-output/implementation-artifacts/` — sprint status and story execution artifacts

## Implementation Roadmap (High Level)

1. Core runtime foundations (CLI, router, workflow engine, agent loop)
2. Safety and policy layer (capabilities, confirmations, backend mapping)
3. Persistence and observability baseline (SQLite + structured logs)
4. Provider contracts and initial adapters
5. Plugin loading and registry extensibility

## Working With This Repo (Now)

At this stage, the most useful workflow is:

1. Review planning docs in `_bmad-output/planning-artifacts/`
2. Select the next story from `_bmad-output/implementation-artifacts/stories/`
3. Implement incrementally and keep sprint status updated

## GitLab CI Baseline

This project uses GitLab CI for merge request quality gates.

- Pipeline definition: `.gitlab-ci.yml`
- Required stages: `lint` → `typecheck` → `test`
- Merge requests are expected to pass all stages before merge.

Run the same checks locally before opening a merge request:

```bash
python -m pip install -e .[dev]
ruff check src tests
mypy src
pytest
```

Troubleshooting (Windows + WSL):

- If `python`, `ruff`, `mypy`, or `pytest` are missing in the host shell, run commands in WSL.
- Create and use a local virtual environment instead of system-wide installs.

```bash
wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi python3 -m venv .venv
wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi .venv/bin/pip install -e ".[dev]"
wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi .venv/bin/ruff check src tests
wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi .venv/bin/mypy src
wsl --cd /home/aabero/code/endava/comunIA/aiSkillsLab-aabero/endi .venv/bin/pytest
```

## Notes

- ENDI is intentionally **human-in-the-loop** for sensitive operations.
- Destructive actions are expected to require explicit confirmation.
- The README will evolve as implementation lands and runnable commands are added.
