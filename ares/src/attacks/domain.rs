use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
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

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
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
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
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

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TargetRule {
    SystemPromptConfidentiality,
    NoMaliciousCode,
    SupportDomainOnly,
    NoDestructiveActionsWithoutConfirmation,
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

#[derive(Debug, Clone, PartialEq, Eq)]
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

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
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

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
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

#[derive(Debug, Clone, PartialEq, Eq)]
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
