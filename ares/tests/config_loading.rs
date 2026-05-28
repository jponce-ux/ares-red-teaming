use std::fs;

use ares::config::{AresConfig, CliConfigOverrides};

#[test]
fn loads_runtime_config_with_endi_defaults() {
    let path = std::env::temp_dir().join(format!("ares-config-{}.toml", std::process::id()));
    fs::write(
        &path,
        r#"
[endi.command]
python_executable = "endi/.venv/bin/python"
working_directory = "endi"
timeout_seconds = 60

[endi.target]
provider = "ollama"
model = "granite4.1:3b"
base_url = "http://localhost:11434"
output = "json"

[runtime]
max_concurrency = 4

[evidence]
output_directory = "ares/reports"
retain_prompts = true
"#,
    )
    .expect("write config");

    let config = AresConfig::load_from_file(&path).expect("config loads");

    assert_eq!(config.endi.target.provider, "ollama");
    assert_eq!(config.endi.target.model, "granite4.1:3b");
    assert_eq!(config.endi.target.base_url, "http://localhost:11434");
    assert_eq!(config.endi.target.output, "json");
    assert_eq!(config.runtime.max_concurrency, 4);
}

#[test]
fn default_config_uses_official_endi_target() {
    let config = AresConfig::default();

    assert_eq!(config.endi.target.provider, "ollama");
    assert_eq!(config.endi.target.model, "granite4.1:3b");
    assert_eq!(config.endi.target.base_url, "http://localhost:11434");
    assert_eq!(config.endi.command.timeout_seconds, 60);
}

#[test]
fn rejects_invalid_runtime_config() {
    let path = std::env::temp_dir().join(format!("ares-bad-config-{}.toml", std::process::id()));
    fs::write(
        &path,
        r#"
[endi.target]
provider = ""
model = ""
base_url = "ftp://not-supported"

[runtime]
max_concurrency = 0
"#,
    )
    .expect("write config");

    let error = AresConfig::load_from_file(&path).expect_err("invalid config");

    assert!(error.to_string().contains("provider"));
    assert!(error.to_string().contains("max_concurrency"));
}

#[test]
fn cli_overrides_take_precedence_over_file_config() {
    let config = AresConfig::default().with_overrides(CliConfigOverrides {
        provider: Some("ollama".to_string()),
        model: Some("mistral".to_string()),
        base_url: Some("http://127.0.0.1:11434".to_string()),
        timeout_seconds: Some(30),
        output_directory: Some("tmp/evidence".to_string()),
    });

    assert_eq!(config.endi.target.model, "mistral");
    assert_eq!(config.endi.target.base_url, "http://127.0.0.1:11434");
    assert_eq!(config.endi.command.timeout_seconds, 30);
    assert_eq!(config.evidence.output_directory, "tmp/evidence");
}
