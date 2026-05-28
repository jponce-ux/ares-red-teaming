pub const HELP_TEXT: &str = "\
ARES red-team CLI

Usage: ares [COMMAND] [OPTIONS]

Commands:
  help        Show this help text
  version     Show the ARES version
";

#[derive(Debug, PartialEq, Eq)]
pub enum CliAction {
    Help,
    Version,
    Stress,
}

pub fn parse_action(args: &[String]) -> CliAction {
    match args.get(1).map(String::as_str) {
        Some("--version" | "-V" | "version") => CliAction::Version,
        Some("stress") => CliAction::Stress,
        _ => CliAction::Help,
    }
}

#[cfg(test)]
mod tests {
    use super::{CliAction, HELP_TEXT, parse_action};

    #[test]
    fn cli_construction_includes_help_and_version_paths() {
        let help_args = vec!["ares".to_string(), "--help".to_string()];
        let version_args = vec!["ares".to_string(), "version".to_string()];

        assert_eq!(parse_action(&help_args), CliAction::Help);
        assert_eq!(parse_action(&version_args), CliAction::Version);
        assert!(HELP_TEXT.contains("ARES red-team CLI"));
    }
}
