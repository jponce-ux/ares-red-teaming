use std::path::Path;

use crate::attacks::domain::{AttackCase, AttackCategory};
use crate::attacks::fixture::{FixtureError, load_attack_fixtures};

pub const FIXTURE_PATH: &str = "ares/fixtures/attacks/prompt_injection.jsonl";

pub fn load(path: &Path) -> Result<Vec<AttackCase>, FixtureError> {
    let attacks = load_attack_fixtures(path)?;
    Ok(attacks
        .into_iter()
        .filter(|attack| attack.category == AttackCategory::PromptInjection)
        .collect())
}
