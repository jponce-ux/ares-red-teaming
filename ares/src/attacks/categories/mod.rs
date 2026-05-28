use crate::attacks::domain::{AttackCase, AttackCategory};

pub mod jailbreak_roleplay;
pub mod prompt_injection;
pub mod system_prompt_extraction;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PreparedAttack {
    pub attack: AttackCase,
    pub category: AttackCategory,
    pub prompt: String,
    pub target_rule: crate::attacks::domain::TargetRule,
    pub expected_violation: String,
}

pub fn prepare_for_execution(attack: AttackCase) -> PreparedAttack {
    PreparedAttack {
        category: attack.category,
        prompt: attack.prompt.clone(),
        target_rule: attack.target_rule,
        expected_violation: attack.expected_violation.as_str().to_string(),
        attack,
    }
}
