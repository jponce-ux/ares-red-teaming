use ares::attacks::domain::{AttackCategory, AttackId, RunId, Severity, TargetRule};
use ares::evaluator::{EvaluationDecision, EvaluationStatus, EvidenceRecord};
use ares::replay::{MitigationStatus, ReplayCandidate, compare_replay};
use ares::reporting::{Report, ReportArtifactStatus, render_markdown_report};

fn candidate(id: &str, status: EvaluationStatus, severity: Option<Severity>) -> ReplayCandidate {
    ReplayCandidate {
        evidence: EvidenceRecord {
            run_id: RunId::new("run").expect("run"),
            attack_id: AttackId::new(id).expect("attack"),
            category: AttackCategory::PromptInjection,
            target_rule: TargetRule::SupportDomainOnly,
            prompt: Some("prompt".to_string()),
            response: Some("response".to_string()),
            command: "endi chat".to_string(),
            exit_code: Some(0),
            timed_out: false,
            harness_error: None,
        },
        decision: EvaluationDecision::new(status, severity, "rationale", None),
    }
}

#[test]
fn replay_comparison_classifies_status_changes() {
    let comparisons = compare_replay(
        &[
            candidate(
                "closed",
                EvaluationStatus::Success,
                Some(Severity::Critical),
            ),
            candidate(
                "reduced",
                EvaluationStatus::Success,
                Some(Severity::Critical),
            ),
            candidate("unchanged", EvaluationStatus::Partial, Some(Severity::Low)),
            candidate("regressed", EvaluationStatus::Blocked, None),
        ],
        &[
            candidate("closed", EvaluationStatus::Blocked, None),
            candidate("reduced", EvaluationStatus::Partial, Some(Severity::Low)),
            candidate("unchanged", EvaluationStatus::Partial, Some(Severity::Low)),
            candidate("regressed", EvaluationStatus::Success, Some(Severity::High)),
            candidate("missing-baseline", EvaluationStatus::Blocked, None),
        ],
    );

    assert_eq!(comparisons[0].status, MitigationStatus::Closed);
    assert_eq!(comparisons[1].status, MitigationStatus::Reduced);
    assert_eq!(comparisons[2].status, MitigationStatus::Unchanged);
    assert_eq!(comparisons[3].status, MitigationStatus::Regressed);
    assert_eq!(comparisons[4].status, MitigationStatus::MissingBaseline);
}

#[test]
fn markdown_report_includes_replay_status_section() {
    let mut report = Report {
        title: "Replay".to_string(),
        run_id: "run".to_string(),
        findings: vec![],
        manual_attacks: ReportArtifactStatus::new("manual.md", true),
        reflections: ReportArtifactStatus::new("reflection.md", true),
        replay: vec![],
    };
    report.replay = vec![
        compare_replay(
            &[candidate(
                "a1",
                EvaluationStatus::Success,
                Some(Severity::Critical),
            )],
            &[candidate("a1", EvaluationStatus::Blocked, None)],
        )[0]
        .clone(),
    ];

    let markdown = render_markdown_report(&report);

    assert!(markdown.contains("## Mitigation Replay"));
    assert!(markdown.contains("Closed"));
}
