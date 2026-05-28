use ares::stress::{StressRunConfig, StressSample, StressStatus, StressSummary};

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
