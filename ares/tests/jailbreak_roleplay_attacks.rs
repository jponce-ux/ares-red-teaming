use std::path::Path;

use ares::attacks::categories::{jailbreak_roleplay, prepare_for_execution};
use ares::attacks::domain::AttackCategory;

#[test]
fn jailbreak_roleplay_fixture_loads_variants() {
    let attacks = jailbreak_roleplay::load(Path::new(jailbreak_roleplay::FIXTURE_PATH))
        .expect("jailbreak fixtures");

    assert!((3..=5).contains(&attacks.len()));
    assert!(
        attacks
            .iter()
            .all(|attack| attack.category == AttackCategory::JailbreakRoleplay)
    );
}

#[test]
fn jailbreak_roleplay_prepared_attack_preserves_evidence_metadata() {
    let attack = jailbreak_roleplay::load(Path::new(jailbreak_roleplay::FIXTURE_PATH))
        .expect("jailbreak fixtures")
        .remove(0);

    let prepared = prepare_for_execution(attack);

    assert_eq!(prepared.category, AttackCategory::JailbreakRoleplay);
    assert!(!prepared.prompt.is_empty());
    assert!(!prepared.expected_violation.is_empty());
}
