use std::sync::{Arc, Mutex};

use ares::attacks::domain::{
    AttackCase, AttackCategory, AttackId, ExpectedViolation, Severity, TargetRule,
};
use ares::runner::{AttackRunner, EndiLikeClient, RunConfig};
use ares::targets::endi::{EndiCommandError, EndiCommandResult};

#[derive(Clone)]
struct FakeClient {
    calls: Arc<Mutex<Vec<String>>>,
}

impl EndiLikeClient for FakeClient {
    fn chat(&self, prompt: &str) -> Result<EndiCommandResult, EndiCommandError> {
        self.calls.lock().expect("calls").push(prompt.to_string());
        Ok(fake_result(prompt, false))
    }
}

fn attack(id: &str, prompt: &str) -> AttackCase {
    AttackCase {
        id: AttackId::new(id).expect("id"),
        category: AttackCategory::PromptInjection,
        prompt: prompt.to_string(),
        target_rule: TargetRule::SupportDomainOnly,
        expected_violation: ExpectedViolation::new("domain drift").expect("violation"),
        severity: Severity::High,
        expected_status: None,
    }
}

fn fake_result(prompt: &str, timed_out: bool) -> EndiCommandResult {
    EndiCommandResult {
        command: format!("endi chat {prompt}"),
        stdout: format!("response to {prompt}"),
        stderr: String::new(),
        exit_code: Some(0),
        started_at: std::time::SystemTime::now(),
        duration_ms: 1,
        timed_out,
        parsed_output: None,
    }
}

#[test]
fn runner_executes_attacks_sequentially_and_preserves_metadata() {
    let calls = Arc::new(Mutex::new(Vec::new()));
    let runner = AttackRunner::new(FakeClient {
        calls: Arc::clone(&calls),
    });
    let attacks = vec![attack("a-1", "first"), attack("a-2", "second")];

    let run = runner.run(attacks, RunConfig::default());

    assert_eq!(calls.lock().expect("calls").as_slice(), ["first", "second"]);
    assert_eq!(run.results.len(), 2);
    assert_eq!(run.results[0].attack_id.as_str(), "a-1");
    assert_eq!(run.results[0].prompt, "first");
    assert_eq!(run.results[0].stdout, "response to first");
}

#[test]
fn runner_continues_after_target_failure() {
    #[derive(Clone)]
    struct FailingOnce {
        calls: Arc<Mutex<usize>>,
    }

    impl EndiLikeClient for FailingOnce {
        fn chat(&self, prompt: &str) -> Result<EndiCommandResult, EndiCommandError> {
            let mut calls = self.calls.lock().expect("calls");
            *calls += 1;
            if *calls == 1 {
                return Err(EndiCommandError::new_for_test("simulated failure"));
            }
            Ok(fake_result(prompt, false))
        }
    }

    let runner = AttackRunner::new(FailingOnce {
        calls: Arc::new(Mutex::new(0)),
    });

    let run = runner.run(
        vec![attack("a-1", "first"), attack("a-2", "second")],
        RunConfig::default(),
    );

    assert_eq!(run.results.len(), 2);
    assert!(
        run.results[0]
            .harness_error
            .as_ref()
            .expect("error")
            .contains("simulated")
    );
    assert_eq!(run.results[1].stdout, "response to second");
}
