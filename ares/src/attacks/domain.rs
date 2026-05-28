use std::fmt;

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(try_from = "String", into = "String")]
pub struct AttackId(String);

impl AttackId {
    pub fn new(value: impl Into<String>) -> Result<Self, DomainParseError> {
        let value = value.into();
        if value.trim().is_empty() {
            Err(DomainParseError::new("attack id must not be empty"))
        } else {
            Ok(Self(value))
        }
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl TryFrom<String> for AttackId {
    type Error = DomainParseError;

    fn try_from(value: String) -> Result<Self, Self::Error> {
        Self::new(value)
    }
}

impl From<AttackId> for String {
    fn from(value: AttackId) -> Self {
        value.0
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(try_from = "String", into = "String")]
pub struct RunId(String);

impl RunId {
    pub fn new(value: impl Into<String>) -> Result<Self, DomainParseError> {
        let value = value.into();
        if value.trim().is_empty() {
            Err(DomainParseError::new("run id must not be empty"))
        } else {
            Ok(Self(value))
        }
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl TryFrom<String> for RunId {
    type Error = DomainParseError;

    fn try_from(value: String) -> Result<Self, Self::Error> {
        Self::new(value)
    }
}

impl From<RunId> for String {
    fn from(value: RunId) -> Self {
        value.0
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum AttackCategory {
    PromptInjection,
    JailbreakRoleplay,
    SystemPromptExtraction,
    MaliciousCode,
    OutOfDomain,
}

impl AttackCategory {
    pub fn parse(value: &str) -> Result<Self, DomainParseError> {
        match value {
            "prompt_injection" => Ok(Self::PromptInjection),
            "jailbreak_roleplay" => Ok(Self::JailbreakRoleplay),
            "system_prompt_extraction" => Ok(Self::SystemPromptExtraction),
            "malicious_code" => Ok(Self::MaliciousCode),
            "out_of_domain" => Ok(Self::OutOfDomain),
            _ => Err(DomainParseError::new(format!("unknown category: {value}"))),
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum TargetRule {
    #[serde(rename = "R1_SYSTEM_PROMPT_CONFIDENTIALITY")]
    SystemPromptConfidentiality,
    #[serde(rename = "R2_NO_MALICIOUS_CODE")]
    NoMaliciousCode,
    #[serde(rename = "R3_SUPPORT_DOMAIN_ONLY")]
    SupportDomainOnly,
    #[serde(rename = "R4_NO_DESTRUCTIVE_ACTIONS_WITHOUT_CONFIRMATION")]
    NoDestructiveActionsWithoutConfirmation,
    #[serde(rename = "R5_NO_FAKE_SECRETS_OR_INTERNAL_DATA")]
    NoFakeSecretsOrInternalData,
}

impl TargetRule {
    pub fn parse(value: &str) -> Result<Self, DomainParseError> {
        match value {
            "R1_SYSTEM_PROMPT_CONFIDENTIALITY" => Ok(Self::SystemPromptConfidentiality),
            "R2_NO_MALICIOUS_CODE" => Ok(Self::NoMaliciousCode),
            "R3_SUPPORT_DOMAIN_ONLY" => Ok(Self::SupportDomainOnly),
            "R4_NO_DESTRUCTIVE_ACTIONS_WITHOUT_CONFIRMATION" => {
                Ok(Self::NoDestructiveActionsWithoutConfirmation)
            }
            "R5_NO_FAKE_SECRETS_OR_INTERNAL_DATA" => Ok(Self::NoFakeSecretsOrInternalData),
            _ => Err(DomainParseError::new(format!(
                "unknown target rule: {value}"
            ))),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(try_from = "String", into = "String")]
pub struct ExpectedViolation(String);

impl ExpectedViolation {
    pub fn new(value: impl Into<String>) -> Result<Self, DomainParseError> {
        let value = value.into();
        if value.trim().is_empty() {
            Err(DomainParseError::new(
                "expected_violation must not be empty",
            ))
        } else {
            Ok(Self(value))
        }
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl TryFrom<String> for ExpectedViolation {
    type Error = DomainParseError;

    fn try_from(value: String) -> Result<Self, Self::Error> {
        Self::new(value)
    }
}

impl From<ExpectedViolation> for String {
    fn from(value: ExpectedViolation) -> Self {
        value.0
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Severity {
    Critical,
    High,
    Medium,
    Low,
}

impl Severity {
    pub fn parse(value: &str) -> Result<Self, DomainParseError> {
        match value {
            "critical" => Ok(Self::Critical),
            "high" => Ok(Self::High),
            "medium" => Ok(Self::Medium),
            "low" => Ok(Self::Low),
            _ => Err(DomainParseError::new(format!("unknown severity: {value}"))),
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ResultStatus {
    Blocked,
    Success,
    Partial,
    Inconclusive,
    TargetError,
    HarnessError,
}

impl ResultStatus {
    pub fn parse(value: &str) -> Result<Self, DomainParseError> {
        match value {
            "blocked" => Ok(Self::Blocked),
            "success" => Ok(Self::Success),
            "partial" => Ok(Self::Partial),
            "inconclusive" => Ok(Self::Inconclusive),
            "target_error" => Ok(Self::TargetError),
            "harness_error" => Ok(Self::HarnessError),
            _ => Err(DomainParseError::new(format!(
                "unknown result status: {value}"
            ))),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct AttackCase {
    pub id: AttackId,
    pub category: AttackCategory,
    pub prompt: String,
    pub target_rule: TargetRule,
    pub expected_violation: ExpectedViolation,
    pub severity: Severity,
    pub expected_status: Option<ResultStatus>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DomainParseError {
    message: String,
}

impl DomainParseError {
    pub fn new(message: impl Into<String>) -> Self {
        Self {
            message: message.into(),
        }
    }
}

impl fmt::Display for DomainParseError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str(&self.message)
    }
}

impl std::error::Error for DomainParseError {}
