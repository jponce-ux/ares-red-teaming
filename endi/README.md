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

## Local Ollama Chat

ENDI can route chat prompts to a local Ollama server. Ollama defaults to
`http://localhost:11434`, and local models do not require API credentials.

```bash
.venv/bin/python -m endi.cli chat "Say hello in one sentence" --provider ollama --model llama3.2
```

Tagged model names are supported:

```bash
.venv/bin/python -m endi.cli chat "Summarize this test" --provider ollama --model gemma4:e2b
```

Use `--base-url` when Ollama is listening on a different local endpoint:

```bash
.venv/bin/python -m endi.cli chat "Say hello" --provider ollama --model mistral --base-url http://127.0.0.1:11434
```

For machine-readable output:

```bash
.venv/bin/python -m endi.cli chat "Say hello" --provider ollama --model llama3.2 --output json
```

When you explicitly select a chat provider, ENDI remembers that provider
configuration for later invocations. For example, after this command:

```bash
.venv/bin/python -m endi.cli chat "Hello" --provider ollama --model granite4.1:3b
```

a later `submit` call uses the remembered local model instead of falling back
to OpenAI:

```bash
.venv/bin/python -m endi.cli submit "test"
```

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
