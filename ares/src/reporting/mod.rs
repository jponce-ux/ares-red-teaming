pub mod markdown;

use std::fs;
use std::path::Path;

use crate::evaluator::{EvaluationDecision, EvidenceRecord};
use crate::replay::ReplayComparison;

pub use markdown::render_markdown_report;

#[derive(Debug, Clone)]
pub struct Report {
    pub title: String,
    pub run_id: String,
    pub findings: Vec<ReportFinding>,
    pub manual_attacks: ReportArtifactStatus,
    pub reflections: ReportArtifactStatus,
    pub replay: Vec<ReplayComparison>,
}

#[derive(Debug, Clone)]
pub struct ReportFinding {
    pub evidence: EvidenceRecord,
    pub decision: EvaluationDecision,
}

#[derive(Debug, Clone)]
pub struct ReportArtifactStatus {
    pub path: String,
    pub complete: bool,
}

impl ReportArtifactStatus {
    pub fn new(path: impl Into<String>, complete: bool) -> Self {
        Self {
            path: path.into(),
            complete,
        }
    }
}

pub fn write_markdown_report(report: &Report, path: &Path) -> std::io::Result<()> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)?;
    }
    fs::write(path, render_markdown_report(report))
}
