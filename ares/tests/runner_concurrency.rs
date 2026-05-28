use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

use ares::attacks::domain::{
    AttackCase, AttackCategory, AttackId, ExpectedViolation, Severity, TargetRule,
};
use ares::runner::{AttackRunner, EndiLikeClient, RunConfig};
use ares::targets::endi::{EndiCommandError, EndiCommandResult};

#[derive(Clone)]
struct TrackingClient {
    active: Arc<Mutex<usize>>,
    max_seen: Arc<Mutex<usize>>,
}

impl EndiLikeClient for TrackingClient {
    fn chat(&self, prompt: &str) -> Result<EndiCommandResult, EndiCommandError> {
        {
            let mut active = self.active.lock().expect("active");
            *active += 1;
            let mut max_seen = self.max_seen.lock().expect("max");
            *max_seen = (*max_seen).max(*active);
        }
        thread::sleep(Duration::from_millis(25));
        {
            let mut active = self.active.lock().expect("active");
            *active -= 1;
        }
        Ok(EndiCommandResult {
            command: format!("endi chat {prompt}"),
            stdout: "ok".to_string(),
            stderr: String::new(),
            exit_code: Some(0),
            started_at: std::time::SystemTime::now(),
            duration_ms: 25,
            timed_out: false,
            parsed_output: None,
        })
    }
}

fn attack(id: &str) -> AttackCase {
    AttackCase {
        id: AttackId::new(id).expect("id"),
        category: AttackCategory::PromptInjection,
        prompt: id.to_string(),
        target_rule: TargetRule::SupportDomainOnly,
        expected_violation: ExpectedViolation::new("domain drift").expect("violation"),
        severity: Severity::High,
        expected_status: None,
    }
}

#[test]
fn runner_bounded_parallel_execution_respects_limit() {
    let max_seen = Arc::new(Mutex::new(0));
    let runner = AttackRunner::new(TrackingClient {
        active: Arc::new(Mutex::new(0)),
        max_seen: Arc::clone(&max_seen),
    });
    let config = RunConfig {
        max_concurrency: 2,
        ..RunConfig::default()
    };

    let run = runner.run_bounded(
        vec![attack("a1"), attack("a2"), attack("a3"), attack("a4")],
        config,
    );

    assert_eq!(run.results.len(), 4);
    assert!(*max_seen.lock().expect("max") <= 2);
}

#[test]
fn runner_preserves_timeout_flag_from_target_result() {
    #[derive(Clone)]
    struct TimeoutClient;

    impl EndiLikeClient for TimeoutClient {
        fn chat(&self, prompt: &str) -> Result<EndiCommandResult, EndiCommandError> {
            Ok(EndiCommandResult {
                command: format!("endi chat {prompt}"),
                stdout: String::new(),
                stderr: String::new(),
                exit_code: None,
                started_at: std::time::SystemTime::now(),
                duration_ms: 50,
                timed_out: true,
                parsed_output: None,
            })
        }
    }

    let runner = AttackRunner::new(TimeoutClient);
    let run = runner.run_bounded(vec![attack("timeout")], RunConfig::default());

    assert!(run.results[0].timed_out);
}
