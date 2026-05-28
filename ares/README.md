# ARES

ARES is the Rust red-team CLI for this repository. ENDI remains a separate
Python target project under `endi/`.

Quality gates from the repository root:

```bash
cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features
cargo test --workspace
```

The current scaffold is dependency-free so it can build in offline Codex
sandbox sessions. The planned production stack remains Cargo plus the Rust
libraries documented in the Spec Kit artifacts when dependency access is
available.
