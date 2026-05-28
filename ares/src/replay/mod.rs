use std::collections::BTreeMap;

use crate::attacks::domain::AttackId;
use crate::evaluator::{EvaluationDecision, EvaluationStatus, EvidenceRecord};

#[derive(Debug, Clone)]
pub struct ReplayCandidate {
    pub evidence: EvidenceRecord,
    pub decision: EvaluationDecision,
}

pub type ReplayBaseline = ReplayCandidate;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum MitigationStatus {
    Closed,
    Reduced,
    Unchanged,
    Regressed,
    MissingBaseline,
    ExecutionError,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MitigationMetadata {
    pub owner: String,
    pub description: String,
}

impl Default for MitigationMetadata {
    fn default() -> Self {
        Self {
            owner: "ENDI".to_string(),
            description: "ENDI target policy/system prompt enforcement".to_string(),
        }
    }
}

#[derive(Debug, Clone)]
pub struct ReplayComparison {
    pub attack_id: AttackId,
    pub baseline_status: Option<EvaluationStatus>,
    pub replay_status: EvaluationStatus,
    pub status: MitigationStatus,
    pub metadata: MitigationMetadata,
}

pub fn compare_replay(
    baseline: &[ReplayCandidate],
    replay: &[ReplayCandidate],
) -> Vec<ReplayComparison> {
    let baseline_by_id: BTreeMap<String, &ReplayCandidate> = baseline
        .iter()
        .map(|candidate| (candidate.evidence.attack_id.as_str().to_string(), candidate))
        .collect();
    replay
        .iter()
        .map(|candidate| {
            let baseline_candidate = baseline_by_id.get(candidate.evidence.attack_id.as_str());
            let status = match baseline_candidate {
                None => MitigationStatus::MissingBaseline,
                Some(previous) => classify(previous.decision.status, candidate.decision.status),
            };
            ReplayComparison {
                attack_id: candidate.evidence.attack_id.clone(),
                baseline_status: baseline_candidate.map(|candidate| candidate.decision.status),
                replay_status: candidate.decision.status,
                status,
                metadata: MitigationMetadata::default(),
            }
        })
        .collect()
}

fn classify(baseline: EvaluationStatus, replay: EvaluationStatus) -> MitigationStatus {
    if matches!(
        replay,
        EvaluationStatus::TargetError | EvaluationStatus::HarnessError
    ) {
        return MitigationStatus::ExecutionError;
    }
    match (baseline, replay) {
        (EvaluationStatus::Success | EvaluationStatus::Partial, EvaluationStatus::Blocked) => {
            MitigationStatus::Closed
        }
        (EvaluationStatus::Success, EvaluationStatus::Partial) => MitigationStatus::Reduced,
        (left, right) if left == right => MitigationStatus::Unchanged,
        (EvaluationStatus::Blocked | EvaluationStatus::Inconclusive, EvaluationStatus::Success)
        | (EvaluationStatus::Blocked | EvaluationStatus::Inconclusive, EvaluationStatus::Partial)
        | (EvaluationStatus::Partial, EvaluationStatus::Success) => MitigationStatus::Regressed,
        _ => MitigationStatus::Unchanged,
    }
}
