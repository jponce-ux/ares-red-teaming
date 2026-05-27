# ARES-to-ENDI Integration Contract

ARES calls ENDI through subprocess execution only. ARES must not import ENDI Python modules.

## Rust Shape

```rust
pub struct EndiClient {
    // command path, working directory, provider config, timeout config
}
```

Required methods:

- `version() -> Result<EndiCommandResult>`
- `chat(prompt, options) -> Result<EndiCommandResult>`
- `submit(prompt, options) -> Result<EndiCommandResult>`
- `validate_environment() -> Result<EndiEnvironmentStatus>`

ARES should prefer `chat` for attack execution.

## Recommended Command Shape

```text
cd endi
.venv/bin/python -m endi.cli chat \
  "<attack prompt>" \
  --provider ollama \
  --model granite4.1:3b \
  --base-url http://localhost:11434 \
  --timeout-seconds 60 \
  --output json \
  --non-interactive
```

## Required Captured Fields

- `attack_id`
- `category`
- `prompt`
- `command`
- `stdout`
- `stderr`
- `exit_code`
- `started_at`
- `duration_ms`
- `timeout`
- `parsed_endi_output`
- `evaluation_decision`
- `severity`
- `evidence`

## Rust Layout

Use a root Cargo workspace with `ares/` as the first Rust binary crate:

```text
ares-red-teaming/
├── Cargo.toml
├── Cargo.lock
├── ares/
│   ├── Cargo.toml
│   └── src/main.rs
└── endi/
    ├── pyproject.toml
    └── src/endi/
```

Root `Cargo.toml`:

```toml
[workspace]
members = ["ares"]
resolver = "2"
```

Run ARES quality gates from the repository root:

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features
cargo test --workspace
```

ENDI remains a separate Python auxiliary project under `endi/` and is not part of the Cargo workspace.
