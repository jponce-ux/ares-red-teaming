use crate::attacks::domain::{AttackCategory, AttackId, RunId, TargetRule};
use crate::runner::AttackRunResult;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EvidenceRecord {
    pub run_id: RunId,
    pub attack_id: AttackId,
    pub category: AttackCategory,
    pub target_rule: TargetRule,
    pub prompt: Option<String>,
    pub response: Option<String>,
    pub command: String,
    pub exit_code: Option<i32>,
    pub timed_out: bool,
    pub harness_error: Option<String>,
}

impl EvidenceRecord {
    pub fn from_run_result(result: &AttackRunResult, retain_prompt_response: bool) -> Self {
        Self {
            run_id: result.run_id.clone(),
            attack_id: result.attack_id.clone(),
            category: result.category,
            target_rule: result.target_rule,
            prompt: retain_prompt_response.then(|| result.prompt.clone()),
            response: retain_prompt_response.then(|| result.stdout.clone()),
            command: result.command.clone(),
            exit_code: result.exit_code,
            timed_out: result.timed_out,
            harness_error: result.harness_error.clone(),
        }
    }
}
