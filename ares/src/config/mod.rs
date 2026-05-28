use std::fs;
use std::path::Path;

use serde::Deserialize;
use thiserror::Error;

#[derive(Debug, Clone, Default, Deserialize, PartialEq, Eq)]
#[serde(default)]
pub struct AresConfig {
    pub endi: EndiConfig,
    pub runtime: RuntimeLimits,
    pub evidence: EvidenceConfig,
}

#[derive(Debug, Clone, Default, Deserialize, PartialEq, Eq)]
#[serde(default)]
pub struct EndiConfig {
    pub command: EndiCommandConfig,
    pub target: EndiTargetConfig,
}

#[derive(Debug, Clone, Deserialize, PartialEq, Eq)]
#[serde(default)]
pub struct EndiCommandConfig {
    pub python_executable: String,
    pub working_directory: String,
    pub timeout_seconds: u64,
}

#[derive(Debug, Clone, Deserialize, PartialEq, Eq)]
#[serde(default)]
pub struct EndiTargetConfig {
    pub provider: String,
    pub model: String,
    pub base_url: String,
    pub output: String,
}

#[derive(Debug, Clone, Deserialize, PartialEq, Eq)]
#[serde(default)]
pub struct RuntimeLimits {
    pub max_concurrency: usize,
    pub attack_fixture: String,
    pub report_path: String,
}

#[derive(Debug, Clone, Deserialize, PartialEq, Eq)]
#[serde(default)]
pub struct EvidenceConfig {
    pub output_directory: String,
    pub retain_prompts: bool,
}

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct CliConfigOverrides {
    pub provider: Option<String>,
    pub model: Option<String>,
    pub base_url: Option<String>,
    pub timeout_seconds: Option<u64>,
    pub output_directory: Option<String>,
    pub attack_fixture: Option<String>,
    pub report_path: Option<String>,
    pub python_executable: Option<String>,
    pub working_directory: Option<String>,
    pub max_concurrency: Option<usize>,
}

#[derive(Debug, Error)]
pub enum ConfigError {
    #[error("failed to read config: {0}")]
    Read(#[from] std::io::Error),
    #[error("failed to parse TOML config: {0}")]
    Parse(#[from] toml::de::Error),
    #[error("invalid config: {0}")]
    Validation(String),
}

impl Default for EndiCommandConfig {
    fn default() -> Self {
        Self {
            python_executable: "endi/.venv/bin/python".to_string(),
            working_directory: "endi".to_string(),
            timeout_seconds: 60,
        }
    }
}

impl Default for EndiTargetConfig {
    fn default() -> Self {
        Self {
            provider: "ollama".to_string(),
            model: "granite4.1:3b".to_string(),
            base_url: "http://localhost:11434".to_string(),
            output: "json".to_string(),
        }
    }
}

impl Default for RuntimeLimits {
    fn default() -> Self {
        Self {
            max_concurrency: 1,
            attack_fixture: "ares/fixtures/attacks/prompt_injection.jsonl".to_string(),
            report_path: "ares/reports/latest.md".to_string(),
        }
    }
}

impl Default for EvidenceConfig {
    fn default() -> Self {
        Self {
            output_directory: "ares/reports".to_string(),
            retain_prompts: true,
        }
    }
}

impl AresConfig {
    pub fn load_from_file(path: &Path) -> Result<Self, ConfigError> {
        let content = fs::read_to_string(path)?;
        let config: Self = toml::from_str(&content)?;
        config.validate()?;
        Ok(config)
    }

    pub fn with_overrides(mut self, overrides: CliConfigOverrides) -> Self {
        if let Some(provider) = overrides.provider {
            self.endi.target.provider = provider;
        }
        if let Some(model) = overrides.model {
            self.endi.target.model = model;
        }
        if let Some(base_url) = overrides.base_url {
            self.endi.target.base_url = base_url;
        }
        if let Some(timeout_seconds) = overrides.timeout_seconds {
            self.endi.command.timeout_seconds = timeout_seconds;
        }
        if let Some(output_directory) = overrides.output_directory {
            self.evidence.output_directory = output_directory;
        }
        if let Some(attack_fixture) = overrides.attack_fixture {
            self.runtime.attack_fixture = attack_fixture;
        }
        if let Some(report_path) = overrides.report_path {
            self.runtime.report_path = report_path;
        }
        if let Some(python_executable) = overrides.python_executable {
            self.endi.command.python_executable = python_executable;
        }
        if let Some(working_directory) = overrides.working_directory {
            self.endi.command.working_directory = working_directory;
        }
        if let Some(max_concurrency) = overrides.max_concurrency {
            self.runtime.max_concurrency = max_concurrency;
        }
        self
    }

    pub fn validate(&self) -> Result<(), ConfigError> {
        let mut errors = Vec::new();
        require_non_empty(
            &mut errors,
            "python_executable",
            &self.endi.command.python_executable,
        );
        require_non_empty(
            &mut errors,
            "working_directory",
            &self.endi.command.working_directory,
        );
        require_non_empty(&mut errors, "provider", &self.endi.target.provider);
        require_non_empty(&mut errors, "model", &self.endi.target.model);
        require_non_empty(
            &mut errors,
            "output_directory",
            &self.evidence.output_directory,
        );
        require_non_empty(&mut errors, "attack_fixture", &self.runtime.attack_fixture);
        require_non_empty(&mut errors, "report_path", &self.runtime.report_path);
        if !self.endi.target.base_url.starts_with("http://")
            && !self.endi.target.base_url.starts_with("https://")
        {
            errors.push("base_url must start with http:// or https://".to_string());
        }
        if self.endi.command.timeout_seconds == 0 {
            errors.push("timeout_seconds must be greater than zero".to_string());
        }
        if self.runtime.max_concurrency == 0 {
            errors.push("max_concurrency must be greater than zero".to_string());
        }
        if self.endi.target.output != "json" {
            errors.push("output must be json for ARES evidence capture".to_string());
        }
        if errors.is_empty() {
            Ok(())
        } else {
            Err(ConfigError::Validation(errors.join("; ")))
        }
    }
}

fn require_non_empty(errors: &mut Vec<String>, field: &str, value: &str) {
    if value.trim().is_empty() {
        errors.push(format!("{field} must not be empty"));
    }
}
