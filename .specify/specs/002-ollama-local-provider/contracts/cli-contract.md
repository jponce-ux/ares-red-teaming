# CLI Contract: Ollama Local Provider for ENDI CLI

## Commands

### `endi chat`

Runs one ENDI chat prompt through the same conversation route used by `endi submit`.

Required or optional inputs:

- `PROMPT`: Optional positional prompt. If omitted, ENDI prompts interactively.
- `--provider ollama`: Selects local Ollama provider.
- `--model <model>`: Selects local model, such as `gemma4:e2b`, `llama3.2`, or `mistral`.
- `--base-url <url>`: Overrides Ollama base URL. Defaults to `http://localhost:11434`.
- `--timeout-seconds <seconds>`: Positive request timeout. Defaults to 30 seconds.
- `--output rich|json`: Selects human-readable or machine-readable output.

Success behavior:

- Rich output prints the model response in the existing result panel.
- JSON output includes `status: "success"`, `route: "conversation"`, and `output` with response text.

Failure behavior:

- Rich output prints a provider error message without a Python traceback.
- JSON output includes `status: "success"` for routed conversation results whose output is an error string, preserving current ENDI dispatch behavior.
- The output string includes the stable provider error code, for example `Provider error (provider_missing_model): ...`.

### `endi submit`

Existing command remains supported with the same Ollama options:

```text
endi submit "hello" --provider ollama --model llama3.2
```

## Provider Resolution

- `--provider ollama --model llama3.2` resolves to Ollama model `llama3.2`.
- `--provider ollama:llama3.2` remains supported.
- `--base-url` overrides only the current invocation.
- No API key is required for Ollama.
