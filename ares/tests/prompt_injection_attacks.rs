use std::path::Path;

use ares::attacks::categories::{prepare_for_execution, prompt_injection};
use ares::attacks::domain::AttackCategory;

#[test]
fn prompt_injection_fixture_loads_variants() {
    let attacks = prompt_injection::load(Path::new(prompt_injection::FIXTURE_PATH))
        .expect("prompt injection fixtures");

    assert!((3..=5).contains(&attacks.len()));
    assert!(
        attacks
            .iter()
            .all(|attack| attack.category == AttackCategory::PromptInjection)
    );
}

#[test]
fn prompt_injection_prepared_attack_preserves_evidence_metadata() {
    let attack = prompt_injection::load(Path::new(prompt_injection::FIXTURE_PATH))
        .expect("prompt injection fixtures")
        .remove(0);

    let prepared = prepare_for_execution(attack);

    assert_eq!(prepared.category, AttackCategory::PromptInjection);
    assert!(!prepared.prompt.is_empty());
    assert!(!prepared.expected_violation.is_empty());
}
