use std::time::{SystemTime, UNIX_EPOCH};

use crate::attacks::domain::{AttackCase, AttackCategory, AttackId, RunId, TargetRule};
use crate::targets::endi::{EndiClient, EndiCommandError, EndiCommandResult, ParsedEndiOutput};
use tokio::sync::Semaphore;
use tracing::{info, warn};

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
        info!(
            run_id = %run_id.as_str(),
            attack_id = %attack.id.as_str(),
            category = ?attack.category,
            target_rule = ?attack.target_rule,
            "executing attack"
        );
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

        match tokio::runtime::Builder::new_multi_thread()
            .enable_time()
            .enable_io()
            .build()
        {
            Ok(runtime) => runtime.block_on(self.run_bounded_async(attacks, config)),
            Err(error) => {
                warn!(error = %error, "falling back to sequential attack execution");
                self.run(attacks, config)
            }
        }
    }

    async fn run_bounded_async(&self, attacks: Vec<AttackCase>, config: RunConfig) -> AttackRun {
        let limit = config.max_concurrency.max(1);
        let semaphore = std::sync::Arc::new(Semaphore::new(limit));
        let mut handles = Vec::with_capacity(attacks.len());
        let run_id = config.run_id.clone();

        for (index, attack) in attacks.into_iter().enumerate() {
            let permit = semaphore
                .clone()
                .acquire_owned()
                .await
                .expect("semaphore remains open while runner owns it");
            let client = self.client.clone();
            let run_id = run_id.clone();
            handles.push(tokio::spawn(async move {
                let _permit = permit;
                let runner = AttackRunner::new(client);
                let result = runner.execute_one(&attack, &run_id);
                (index, result)
            }));
        }

        let mut indexed_results = Vec::with_capacity(handles.len());
        for handle in handles {
            match handle.await {
                Ok(result) => indexed_results.push(result),
                Err(error) => warn!(error = %error, "attack task failed to join"),
            }
        }
        indexed_results.sort_by_key(|(index, _)| *index);

        AttackRun {
            run_id: config.run_id,
            results: indexed_results
                .into_iter()
                .map(|(_, result)| result)
                .collect(),
        }
    }
}
