# Data Model: Ollama Local Provider for ENDI CLI

## OllamaProviderConfig

Represents the resolved local provider settings for one ENDI prompt.

Fields:

- `provider`: Must resolve to `ollama`.
- `model`: Non-empty local model name, for example `gemma4:e2b`, `llama3.2`, or `mistral`.
- `base_url`: Non-empty HTTP URL; defaults to `http://localhost:11434`.
- `timeout_seconds`: Positive number of seconds.

Validation:

- Empty provider input is not treated as Ollama.
- Provider value `ollama` is valid when paired with a model.
- Provider value `ollama:<model>` remains valid for backward compatibility.
- Empty or whitespace-only model names are rejected by falling back to provider-derived or default model behavior.

## OllamaPromptRequest

Represents one prompt sent through the ENDI chat provider contract.

Fields:

- `messages`: Ordered chat messages with role and content.
- `stream`: Always false for this feature.
- `model`: Resolved local model name.

Validation:

- User content is converted into a chat message.
- Prompt text is not logged as a secret or credential.

## ProviderErrorCategory

Represents stable error categories exposed by the provider adapter and CLI.

Values:

- `provider_connection_failed`
- `provider_missing_model`
- `timeout`
- `provider_malformed_response`
- `provider_failure`

Validation:

- Missing model is used only when Ollama response data identifies an unavailable model or model-not-found condition.
- Malformed response is used for invalid JSON, non-object JSON, missing message object, or missing response text.
