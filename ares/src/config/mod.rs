use std::collections::BTreeMap;
use std::fmt;
use std::fs;
use std::path::Path;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AresConfig {
    pub endi: EndiConfig,
    pub runtime: RuntimeLimits,
    pub evidence: EvidenceConfig,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EndiConfig {
    pub command: EndiCommandConfig,
    pub target: EndiTargetConfig,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EndiCommandConfig {
    pub python_executable: String,
    pub working_directory: String,
    pub timeout_seconds: u64,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EndiTargetConfig {
    pub provider: String,
    pub model: String,
    pub base_url: String,
    pub output: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RuntimeLimits {
    pub max_concurrency: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
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
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ConfigError {
    messages: Vec<String>,
}

impl ConfigError {
    fn new(message: impl Into<String>) -> Self {
        Self {
            messages: vec![message.into()],
        }
    }

    fn validation(messages: Vec<String>) -> Self {
        Self { messages }
    }
}

impl fmt::Display for ConfigError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str(&self.messages.join("; "))
    }
}

impl std::error::Error for ConfigError {}

impl Default for AresConfig {
    fn default() -> Self {
        Self {
            endi: EndiConfig {
                command: EndiCommandConfig {
                    python_executable: "endi/.venv/bin/python".to_string(),
                    working_directory: "endi".to_string(),
                    timeout_seconds: 60,
                },
                target: EndiTargetConfig {
                    provider: "ollama".to_string(),
                    model: "granite4.1:3b".to_string(),
                    base_url: "http://localhost:11434".to_string(),
                    output: "json".to_string(),
                },
            },
            runtime: RuntimeLimits { max_concurrency: 1 },
            evidence: EvidenceConfig {
                output_directory: "ares/reports".to_string(),
                retain_prompts: true,
            },
        }
    }
}

impl AresConfig {
    pub fn load_from_file(path: &Path) -> Result<Self, ConfigError> {
        let content = fs::read_to_string(path)
            .map_err(|error| ConfigError::new(format!("failed to read config: {error}")))?;
        let mut config = Self::default();
        let values = parse_flat_toml(&content)?;

        set_string(
            &mut config.endi.command.python_executable,
            &values,
            "endi.command.python_executable",
        );
        set_string(
            &mut config.endi.command.working_directory,
            &values,
            "endi.command.working_directory",
        );
        set_u64(
            &mut config.endi.command.timeout_seconds,
            &values,
            "endi.command.timeout_seconds",
        )?;
        set_string(
            &mut config.endi.target.provider,
            &values,
            "endi.target.provider",
        );
        set_string(&mut config.endi.target.model, &values, "endi.target.model");
        set_string(
            &mut config.endi.target.base_url,
            &values,
            "endi.target.base_url",
        );
        set_string(
            &mut config.endi.target.output,
            &values,
            "endi.target.output",
        );
        set_usize(
            &mut config.runtime.max_concurrency,
            &values,
            "runtime.max_concurrency",
        )?;
        set_string(
            &mut config.evidence.output_directory,
            &values,
            "evidence.output_directory",
        );
        set_bool(
            &mut config.evidence.retain_prompts,
            &values,
            "evidence.retain_prompts",
        )?;

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
            Err(ConfigError::validation(errors))
        }
    }
}

fn require_non_empty(errors: &mut Vec<String>, field: &str, value: &str) {
    if value.trim().is_empty() {
        errors.push(format!("{field} must not be empty"));
    }
}

fn parse_flat_toml(content: &str) -> Result<BTreeMap<String, String>, ConfigError> {
    let mut section = String::new();
    let mut values = BTreeMap::new();
    for raw_line in content.lines() {
        let line = raw_line.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        if line.starts_with('[') && line.ends_with(']') {
            section = line
                .trim_start_matches('[')
                .trim_end_matches(']')
                .to_string();
            continue;
        }
        let Some((key, raw_value)) = line.split_once('=') else {
            return Err(ConfigError::new(format!("invalid config line: {line}")));
        };
        let full_key = if section.is_empty() {
            key.trim().to_string()
        } else {
            format!("{}.{}", section, key.trim())
        };
        values.insert(full_key, clean_value(raw_value));
    }
    Ok(values)
}

fn clean_value(raw: &str) -> String {
    raw.trim().trim_matches('"').to_string()
}

fn set_string(target: &mut String, values: &BTreeMap<String, String>, key: &str) {
    if let Some(value) = values.get(key) {
        *target = value.clone();
    }
}

fn set_u64(
    target: &mut u64,
    values: &BTreeMap<String, String>,
    key: &str,
) -> Result<(), ConfigError> {
    if let Some(value) = values.get(key) {
        *target = value
            .parse()
            .map_err(|_| ConfigError::new(format!("{key} must be an integer")))?;
    }
    Ok(())
}

fn set_usize(
    target: &mut usize,
    values: &BTreeMap<String, String>,
    key: &str,
) -> Result<(), ConfigError> {
    if let Some(value) = values.get(key) {
        *target = value
            .parse()
            .map_err(|_| ConfigError::new(format!("{key} must be an integer")))?;
    }
    Ok(())
}

fn set_bool(
    target: &mut bool,
    values: &BTreeMap<String, String>,
    key: &str,
) -> Result<(), ConfigError> {
    if let Some(value) = values.get(key) {
        *target = value
            .parse()
            .map_err(|_| ConfigError::new(format!("{key} must be true or false")))?;
    }
    Ok(())
}
