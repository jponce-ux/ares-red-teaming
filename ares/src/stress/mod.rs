use std::fmt;

use crate::attacks::domain::{
    AttackCase, AttackCategory, AttackId, ExpectedViolation, RunId, Severity, TargetRule,
};
use crate::runner::{AttackRunResult, AttackRunner, EndiLikeClient, RunConfig};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct StressRunConfig {
    pub requests: usize,
    pub concurrency: usize,
}

impl StressRunConfig {
    pub fn new(requests: usize, concurrency: usize) -> Result<Self, StressConfigError> {
        if requests == 0 {
            return Err(StressConfigError::new("requests must be greater than zero"));
        }
        if concurrency == 0 {
            return Err(StressConfigError::new(
                "concurrency must be greater than zero",
            ));
        }
        Ok(Self {
            requests,
            concurrency: concurrency.min(requests),
        })
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct StressTargetConfig {
    pub provider: String,
    pub model: String,
    pub base_url: String,
}

impl Default for StressTargetConfig {
    fn default() -> Self {
        Self {
            provider: "ollama".to_string(),
            model: "granite4.1:3b".to_string(),
            base_url: "http://localhost:11434".to_string(),
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum StressStatus {
    Success,
    TargetError,
    HarnessError,
    Timeout,
    NonZeroExit,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct StressSample {
    pub latency_ms: u128,
    pub status: StressStatus,
}

impl StressSample {
    pub fn new(latency_ms: u128, status: StressStatus) -> Self {
        Self { latency_ms, status }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct StressSummary {
    pub total: usize,
    pub success_count: usize,
    pub target_error_count: usize,
    pub harness_error_count: usize,
    pub timeout_count: usize,
    pub non_zero_exit_count: usize,
    pub max_latency_ms: u128,
}

impl StressSummary {
    pub fn from_samples(samples: Vec<StressSample>) -> Self {
        let mut summary = Self {
            total: samples.len(),
            success_count: 0,
            target_error_count: 0,
            harness_error_count: 0,
            timeout_count: 0,
            non_zero_exit_count: 0,
            max_latency_ms: 0,
        };
        for sample in samples {
            summary.max_latency_ms = summary.max_latency_ms.max(sample.latency_ms);
            match sample.status {
                StressStatus::Success => summary.success_count += 1,
                StressStatus::TargetError => summary.target_error_count += 1,
                StressStatus::HarnessError => summary.harness_error_count += 1,
                StressStatus::Timeout => summary.timeout_count += 1,
                StressStatus::NonZeroExit => summary.non_zero_exit_count += 1,
            }
        }
        summary
    }
}

pub fn run_stress<C>(client: C, prompt: &str, config: StressRunConfig) -> StressSummary
where
    C: EndiLikeClient + Send + 'static,
{
    let attacks = (1..=config.requests)
        .map(|index| stress_attack(index, prompt))
        .collect();
    let run = AttackRunner::new(client).run_bounded(
        attacks,
        RunConfig {
            run_id: RunId::new("stress-run").expect("static run id is valid"),
            max_concurrency: config.concurrency,
        },
    );
    StressSummary::from_samples(run.results.into_iter().map(sample_from_result).collect())
}

fn stress_attack(index: usize, prompt: &str) -> AttackCase {
    AttackCase {
        id: AttackId::new(format!("stress-{index:04}")).expect("generated attack id is valid"),
        category: AttackCategory::OutOfDomain,
        prompt: format!("{prompt} #{index}"),
        target_rule: TargetRule::SupportDomainOnly,
        expected_violation: ExpectedViolation::new("stress execution failure")
            .expect("static expected violation is valid"),
        severity: Severity::Low,
        expected_status: None,
    }
}

fn sample_from_result(result: AttackRunResult) -> StressSample {
    let status = if result.harness_error.is_some() {
        StressStatus::HarnessError
    } else if result.timed_out {
        StressStatus::Timeout
    } else if result.exit_code.is_some_and(|code| code != 0) {
        StressStatus::NonZeroExit
    } else if result
        .parsed_endi_output
        .as_ref()
        .is_some_and(|output| output.status != "ok" && output.status != "success")
    {
        StressStatus::TargetError
    } else {
        StressStatus::Success
    };
    StressSample::new(result.duration_ms, status)
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct StressConfigError {
    message: String,
}

impl StressConfigError {
    fn new(message: impl Into<String>) -> Self {
        Self {
            message: message.into(),
        }
    }
}

impl fmt::Display for StressConfigError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str(&self.message)
    }
}

impl std::error::Error for StressConfigError {}
