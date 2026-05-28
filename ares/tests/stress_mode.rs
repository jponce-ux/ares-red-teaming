use ares::runner::EndiLikeClient;
use ares::stress::{StressRunConfig, StressSample, StressStatus, StressSummary, run_stress};
use ares::targets::endi::{EndiCommandError, EndiCommandResult, ParsedEndiOutput};

#[test]
fn stress_summary_aggregates_status_and_latency() {
    let summary = StressSummary::from_samples(vec![
        StressSample::new(10, StressStatus::Success),
        StressSample::new(20, StressStatus::TargetError),
        StressSample::new(30, StressStatus::HarnessError),
        StressSample::new(40, StressStatus::Timeout),
        StressSample::new(50, StressStatus::NonZeroExit),
    ]);

    assert_eq!(summary.total, 5);
    assert_eq!(summary.success_count, 1);
    assert_eq!(summary.target_error_count, 1);
    assert_eq!(summary.harness_error_count, 1);
    assert_eq!(summary.timeout_count, 1);
    assert_eq!(summary.non_zero_exit_count, 1);
    assert_eq!(summary.max_latency_ms, 50);
}

#[test]
fn stress_config_enforces_bounded_concurrency() {
    let config = StressRunConfig::new(10, 3).expect("valid config");

    assert_eq!(config.requests, 10);
    assert_eq!(config.concurrency, 3);
    assert!(StressRunConfig::new(1, 0).is_err());
}

#[test]
fn stress_mode_executes_repeated_prompts_through_endi_contract() {
    #[derive(Clone)]
    struct StressClient;

    impl EndiLikeClient for StressClient {
        fn chat(&self, prompt: &str) -> Result<EndiCommandResult, EndiCommandError> {
            let index: usize = prompt
                .rsplit_once('#')
                .and_then(|(_, suffix)| suffix.parse().ok())
                .unwrap_or(0);
            Ok(EndiCommandResult {
                command: format!("endi chat {prompt}"),
                stdout: String::new(),
                stderr: String::new(),
                exit_code: Some(if index == 2 { 1 } else { 0 }),
                started_at: std::time::SystemTime::now(),
                duration_ms: 5 + index as u128,
                timed_out: index == 3,
                parsed_output: Some(ParsedEndiOutput {
                    route: "conversation".to_string(),
                    output: Some("ok".to_string()),
                    status: if index == 4 { "error" } else { "ok" }.to_string(),
                }),
            })
        }
    }

    let summary = run_stress(
        StressClient,
        "health check",
        StressRunConfig::new(4, 2).expect("valid config"),
    );

    assert_eq!(summary.total, 4);
    assert_eq!(summary.success_count, 1);
    assert_eq!(summary.non_zero_exit_count, 1);
    assert_eq!(summary.timeout_count, 1);
    assert_eq!(summary.target_error_count, 1);
}
