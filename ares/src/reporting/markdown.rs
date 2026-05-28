use crate::attacks::domain::Severity;
use crate::evaluator::EvaluationStatus;
use crate::reporting::{Report, ReportArtifactStatus};

pub fn render_markdown_report(report: &Report) -> String {
    let mut output = String::new();
    output.push_str(&format!("# {}\n\n", report.title));
    output.push_str(&format!("Run ID: `{}`\n\n", report.run_id));
    output.push_str("## Executive Summary\n\n");
    output.push_str(&format!("Total results: {}\n\n", report.findings.len()));
    output.push_str("## Run Status Summary\n\n");
    for status in [
        EvaluationStatus::Blocked,
        EvaluationStatus::Success,
        EvaluationStatus::Partial,
        EvaluationStatus::Inconclusive,
        EvaluationStatus::TargetError,
        EvaluationStatus::HarnessError,
    ] {
        output.push_str(&format!(
            "- {:?}: {}\n",
            status,
            report
                .findings
                .iter()
                .filter(|finding| finding.decision.status == status)
                .count()
        ));
    }
    output.push('\n');
    output.push_str("## Severity Counts\n\n");
    for severity in [
        Severity::Critical,
        Severity::High,
        Severity::Medium,
        Severity::Low,
    ] {
        output.push_str(&format!(
            "- {:?}: {}\n",
            severity,
            report
                .findings
                .iter()
                .filter(|finding| finding.decision.severity == Some(severity))
                .count()
        ));
    }
    output.push('\n');
    output.push_str("## Vulnerabilities\n\n");
    for finding in &report.findings {
        output.push_str(&format!("### {}\n\n", finding.evidence.attack_id.as_str()));
        output.push_str(&format!("- Status: {:?}\n", finding.decision.status));
        output.push_str(&format!("- Severity: {:?}\n", finding.decision.severity));
        output.push_str(&format!("- Category: {:?}\n", finding.evidence.category));
        output.push_str(&format!(
            "- Target rule: {:?}\n",
            finding.evidence.target_rule
        ));
        output.push_str(&format!("- Rationale: {}\n", finding.decision.rationale));
        match finding.evidence.response.as_deref() {
            Some(response) => output.push_str(&format!("- Evidence response: `{}`\n", response)),
            None => output.push_str("- Evidence response: redacted\n"),
        }
        output.push('\n');
    }
    output.push_str("## Baseline And Replay\n\n");
    output.push_str(
        "Baseline and mitigation replay comparisons should be attached when available.\n\n",
    );
    output.push_str("## Mitigation Replay\n\n");
    if report.replay.is_empty() {
        output.push_str("No mitigation replay comparisons are attached.\n\n");
    } else {
        for comparison in &report.replay {
            output.push_str(&format!(
                "- `{}`: {:?} (baseline: {:?}, replay: {:?})\n",
                comparison.attack_id.as_str(),
                comparison.status,
                comparison.baseline_status,
                comparison.replay_status
            ));
        }
        output.push('\n');
    }
    output.push_str("## Mitigation Suggestions\n\n");
    output.push_str("- Add or strengthen ENDI target policy/system prompt enforcement.\n");
    output.push_str("- Replay successful and partial attacks after mitigation.\n\n");
    output.push_str("## Manual Evidence And Reflections\n\n");
    append_artifact_status(&mut output, "Manual attacks", &report.manual_attacks);
    append_artifact_status(&mut output, "Reflection checkpoints", &report.reflections);
    output.push('\n');
    output.push_str("## Limitations\n\n");
    output.push_str("- Deterministic heuristics are conservative and may classify ambiguous outputs as inconclusive.\n");
    output.push_str("- Execution failures are statuses, not vulnerability severities.\n");
    output
}

fn append_artifact_status(output: &mut String, label: &str, status: &ReportArtifactStatus) {
    output.push_str(&format!(
        "- {label}: `{}` ({})\n",
        status.path,
        if status.complete {
            "complete"
        } else {
            "incomplete"
        }
    ));
}
