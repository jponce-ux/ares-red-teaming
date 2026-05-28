use std::time::{SystemTime, UNIX_EPOCH};
use std::{sync::mpsc, thread};

use crate::attacks::domain::{AttackCase, AttackCategory, AttackId, RunId, TargetRule};
use crate::targets::endi::{EndiClient, EndiCommandError, EndiCommandResult, ParsedEndiOutput};

pub trait EndiLikeClient: Clone {
    fn chat(&self, prompt: &str) -> Result<EndiCommandResult, EndiCommandError>;
}

impl EndiLikeClient for EndiClient {
    fn chat(&self, prompt: &str) -> Result<EndiCommandResult, EndiCommandError> {
        EndiClient::chat(self, prompt)
    }
}

#[derive(Debug, Clone)]
pub struct RunConfig {
    pub run_id: RunId,
    pub max_concurrency: usize,
}

impl Default for RunConfig {
    fn default() -> Self {
        let epoch_ms = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|duration| duration.as_millis())
            .unwrap_or(0);
        Self {
            run_id: RunId::new(format!("run-{epoch_ms}")).expect("generated run id is non-empty"),
            max_concurrency: 1,
        }
    }
}

#[derive(Debug, Clone)]
pub struct AttackRun {
    pub run_id: RunId,
    pub results: Vec<AttackRunResult>,
}

#[derive(Debug, Clone)]
pub struct AttackRunResult {
    pub run_id: RunId,
    pub attack_id: AttackId,
    pub category: AttackCategory,
    pub prompt: String,
    pub target_rule: TargetRule,
    pub command: String,
    pub stdout: String,
    pub stderr: String,
    pub exit_code: Option<i32>,
    pub started_at: SystemTime,
    pub duration_ms: u128,
    pub timed_out: bool,
    pub parsed_endi_output: Option<ParsedEndiOutput>,
    pub harness_error: Option<String>,
}

#[derive(Debug, Clone)]
pub struct AttackRunner<C> {
    client: C,
}

impl<C> AttackRunner<C>
where
    C: EndiLikeClient,
{
    pub fn new(client: C) -> Self {
        Self { client }
    }

    pub fn run(&self, attacks: Vec<AttackCase>, config: RunConfig) -> AttackRun {
        let mut results = Vec::with_capacity(attacks.len());
        for attack in attacks {
            results.push(self.execute_one(&attack, &config.run_id));
        }
        AttackRun {
            run_id: config.run_id,
            results,
        }
    }

    fn execute_one(&self, attack: &AttackCase, run_id: &RunId) -> AttackRunResult {
        match self.client.chat(&attack.prompt) {
            Ok(result) => AttackRunResult {
                run_id: run_id.clone(),
                attack_id: attack.id.clone(),
                category: attack.category,
                prompt: attack.prompt.clone(),
                target_rule: attack.target_rule,
                command: result.command,
                stdout: result.stdout,
                stderr: result.stderr,
                exit_code: result.exit_code,
                started_at: result.started_at,
                duration_ms: result.duration_ms,
                timed_out: result.timed_out,
                parsed_endi_output: result.parsed_output,
                harness_error: None,
            },
            Err(error) => AttackRunResult {
                run_id: run_id.clone(),
                attack_id: attack.id.clone(),
                category: attack.category,
                prompt: attack.prompt.clone(),
                target_rule: attack.target_rule,
                command: String::new(),
                stdout: String::new(),
                stderr: String::new(),
                exit_code: None,
                started_at: SystemTime::now(),
                duration_ms: 0,
                timed_out: false,
                parsed_endi_output: None,
                harness_error: Some(error.to_string()),
            },
        }
    }
}

impl<C> AttackRunner<C>
where
    C: EndiLikeClient + Send + 'static,
{
    pub fn run_bounded(&self, attacks: Vec<AttackCase>, config: RunConfig) -> AttackRun {
        if config.max_concurrency <= 1 || attacks.len() <= 1 {
            return self.run(attacks, config);
        }

        let limit = config.max_concurrency.max(1);
        let (sender, receiver) = mpsc::channel();
        let mut handles = Vec::new();
        let run_id = config.run_id.clone();

        for chunk in attacks.chunks(limit) {
            for attack in chunk {
                let attack = attack.clone();
                let client = self.client.clone();
                let sender = sender.clone();
                let run_id = run_id.clone();
                handles.push(thread::spawn(move || {
                    let runner = AttackRunner::new(client);
                    let result = runner.execute_one(&attack, &run_id);
                    let _ = sender.send(result);
                }));
            }
            for handle in handles.drain(..) {
                let _ = handle.join();
            }
        }
        drop(sender);

        AttackRun {
            run_id: config.run_id,
            results: receiver.into_iter().collect(),
        }
    }
}
