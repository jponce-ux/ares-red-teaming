use clap::{Parser, Subcommand};

pub const HELP_TEXT: &str = "\
ARES red-team CLI

Usage: ares [COMMAND] [OPTIONS]

Commands:
  help        Show this help text
  version     Show the ARES version
  stress      Run controlled ENDI stress tests
";

#[derive(Debug, Parser, PartialEq, Eq)]
#[command(name = "ares", about = "ARES red-team CLI")]
pub struct Cli {
    #[command(subcommand)]
    pub command: Option<Command>,

    #[arg(long)]
    pub run_id: Option<String>,
}

#[derive(Debug, Clone, Subcommand, PartialEq, Eq)]
pub enum Command {
    Version,
    Stress,
}

#[derive(Debug, PartialEq, Eq)]
pub enum CliAction {
    Help,
    Version,
    Stress,
}

impl From<Option<Command>> for CliAction {
    fn from(command: Option<Command>) -> Self {
        match command {
            Some(Command::Version) => Self::Version,
            Some(Command::Stress) => Self::Stress,
            None => Self::Help,
        }
    }
}

pub fn parse_action(args: &[String]) -> CliAction {
    if matches!(args.get(1).map(String::as_str), Some("--version" | "-V")) {
        return CliAction::Version;
    }
    if matches!(args.get(1).map(String::as_str), Some("help")) {
        return CliAction::Help;
    }
    let cli = Cli::try_parse_from(args).unwrap_or(Cli {
        command: None,
        run_id: None,
    });
    cli.command.into()
}

#[cfg(test)]
mod tests {
    use super::{Cli, CliAction, HELP_TEXT, parse_action};
    use clap::Parser;

    #[test]
    fn cli_construction_includes_help_and_version_paths() {
        let help_args = vec!["ares".to_string(), "--help".to_string()];
        let version_args = vec!["ares".to_string(), "version".to_string()];

        assert_eq!(parse_action(&help_args), CliAction::Help);
        assert_eq!(parse_action(&version_args), CliAction::Version);
        assert!(HELP_TEXT.contains("ARES red-team CLI"));
    }

    #[test]
    fn clap_accepts_run_id_override() {
        let cli = Cli::parse_from(["ares", "--run-id", "run-custom", "stress"]);

        assert_eq!(cli.run_id.as_deref(), Some("run-custom"));
    }
}
