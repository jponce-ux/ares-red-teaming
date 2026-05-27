# Quickstart: Ollama Local Provider for ENDI CLI

## Prerequisites

- ENDI development environment installed under `endi/.venv`.
- Optional for manual testing: Ollama running locally with at least one model pulled.

## Manual Local Test

From the repository root:

```bash
cd endi
.venv/bin/python -m endi.cli chat "Say hello in one sentence" --provider ollama --model llama3.2
```

With an alternate local endpoint:

```bash
cd endi
.venv/bin/python -m endi.cli chat "Say hello" --provider ollama --model mistral --base-url http://127.0.0.1:11434
```

Machine-readable output:

```bash
cd endi
.venv/bin/python -m endi.cli chat "Say hello" --provider ollama --model llama3.2 --output json
```

Existing submit path remains valid:

```bash
cd endi
.venv/bin/python -m endi.cli submit "Say hello" --provider ollama --model llama3.2
```

## Validation

Run ENDI gates from `endi/`:

```bash
.venv/bin/python -m pytest -q
.venv/bin/ruff check src tests
.venv/bin/mypy src
```
