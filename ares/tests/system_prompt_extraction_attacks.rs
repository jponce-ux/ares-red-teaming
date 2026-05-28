use std::path::Path;

use ares::attacks::categories::{prepare_for_execution, system_prompt_extraction};
use ares::attacks::domain::AttackCategory;

#[test]
fn system_prompt_extraction_fixture_loads_variants() {
    let attacks = system_prompt_extraction::load(Path::new(system_prompt_extraction::FIXTURE_PATH))
        .expect("system prompt extraction fixtures");

    assert!((3..=5).contains(&attacks.len()));
    assert!(
        attacks
            .iter()
            .all(|attack| attack.category == AttackCategory::SystemPromptExtraction)
    );
}

#[test]
fn system_prompt_extraction_prepared_attack_preserves_evidence_metadata() {
    let attack = system_prompt_extraction::load(Path::new(system_prompt_extraction::FIXTURE_PATH))
        .expect("system prompt extraction fixtures")
        .remove(0);

    let prepared = prepare_for_execution(attack);

    assert_eq!(prepared.category, AttackCategory::SystemPromptExtraction);
    assert!(!prepared.prompt.is_empty());
    assert!(!prepared.expected_violation.is_empty());
}
