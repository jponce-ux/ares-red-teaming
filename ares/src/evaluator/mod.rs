pub mod evidence;
pub mod heuristics;

pub use evidence::EvidenceRecord;

use crate::attacks::domain::Severity;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EvaluationStatus {
    Blocked,
    Success,
    Partial,
    Inconclusive,
    TargetError,
    HarnessError,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct HeuristicMatch {
    pub id: String,
}

impl HeuristicMatch {
    pub fn new(id: impl Into<String>) -> Self {
        Self { id: id.into() }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EvaluationDecision {
    pub status: EvaluationStatus,
    pub severity: Option<Severity>,
    pub rationale: String,
    pub heuristic_match: Option<HeuristicMatch>,
}

impl EvaluationDecision {
    pub fn new(
        status: EvaluationStatus,
        severity: Option<Severity>,
        rationale: impl Into<String>,
        heuristic_match: Option<HeuristicMatch>,
    ) -> Self {
        let severity = match status {
            EvaluationStatus::Success | EvaluationStatus::Partial => severity,
            _ => None,
        };
        Self {
            status,
            severity,
            rationale: rationale.into(),
            heuristic_match,
        }
    }
}

pub fn evaluate(evidence: &EvidenceRecord) -> EvaluationDecision {
    heuristics::evaluate_with_heuristics(evidence)
}
