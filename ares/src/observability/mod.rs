pub mod redaction;

use std::collections::BTreeMap;
use std::fmt;
use std::time::{SystemTime, UNIX_EPOCH};

pub use redaction::redact_sensitive_fields;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RunId(String);

impl RunId {
    pub fn generate() -> Self {
        let epoch_ms = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|duration| duration.as_millis())
            .unwrap_or(0);
        Self(format!("run-{epoch_ms}"))
    }

    pub fn parse(value: &str) -> Result<Self, ObservabilityError> {
        if value.trim().is_empty() {
            Err(ObservabilityError::new("run id must not be empty"))
        } else {
            Ok(Self(value.to_string()))
        }
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct ObservabilityConfig {
    pub retain_sensitive_fields: bool,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct StructuredEvent {
    pub stage: String,
    pub run_id: RunId,
    pub fields: BTreeMap<String, String>,
}

pub fn structured_event(
    stage: impl Into<String>,
    run_id: RunId,
    fields: Vec<(String, String)>,
    config: ObservabilityConfig,
) -> StructuredEvent {
    let fields = if config.retain_sensitive_fields {
        fields.into_iter().collect()
    } else {
        redact_sensitive_fields(fields)
    };
    StructuredEvent {
        stage: stage.into(),
        run_id,
        fields,
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ObservabilityError {
    message: String,
}

impl ObservabilityError {
    fn new(message: impl Into<String>) -> Self {
        Self {
            message: message.into(),
        }
    }
}

impl fmt::Display for ObservabilityError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str(&self.message)
    }
}

impl std::error::Error for ObservabilityError {}
