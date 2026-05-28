use clap::{Parser, Subcommand};

pub const HELP_TEXT: &str = "\
ARES red-team CLI

Usage: ares [COMMAND] [OPTIONS]

Commands:
  help        Show this help text
  version     Show the ARES version
  run         Execute attack fixtures and write a Markdown report
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
    Run(RunArgs),
    Stress(StressArgs),
}

#[derive(Debug, Clone, Parser, PartialEq, Eq)]
pub struct RunArgs {
    #[arg(long)]
    pub run_id: Option<String>,

    #[arg(long)]
    pub fixture: String,

    #[arg(long)]
    pub report: String,

    #[arg(long, default_value_t = 1)]
    pub concurrency: usize,

    #[arg(long, default_value = "endi/.venv/bin/python")]
    pub python_executable: String,

    #[arg(long, default_value = "endi")]
    pub working_directory: String,

    #[arg(long, default_value_t = 60)]
    pub timeout_seconds: u64,

    #[arg(long, default_value = "ollama")]
    pub provider: String,

    #[arg(long, default_value = "granite4.1:3b")]
    pub model: String,

    #[arg(long, default_value = "http://localhost:11434")]
    pub base_url: String,
}

#[derive(Debug, Clone, Parser, PartialEq, Eq)]
pub struct StressArgs {
    #[arg(long, default_value_t = 1)]
    pub requests: usize,

    #[arg(long, default_value_t = 1)]
    pub concurrency: usize,

    #[arg(long, default_value = "ARES safe ENDI stress health check")]
    pub prompt: String,

    #[arg(long, default_value = "endi/.venv/bin/python")]
    pub python_executable: String,

    #[arg(long, default_value = "endi")]
    pub working_directory: String,

    #[arg(long, default_value_t = 60)]
    pub timeout_seconds: u64,

    #[arg(long, default_value = "ollama")]
    pub provider: String,

    #[arg(long, default_value = "granite4.1:3b")]
    pub model: String,

    #[arg(long, default_value = "http://localhost:11434")]
    pub base_url: String,
}

#[derive(Debug, PartialEq, Eq)]
pub enum CliAction {
    Help,
    Version,
    Run(RunArgs),
    Stress(StressArgs),
}

impl From<Option<Command>> for CliAction {
    fn from(command: Option<Command>) -> Self {
        match command {
            Some(Command::Version) => Self::Version,
            Some(Command::Run(args)) => Self::Run(args),
            Some(Command::Stress(args)) => Self::Stress(args),
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
    use super::{Cli, CliAction, HELP_TEXT, StressArgs, parse_action};
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

    #[test]
    fn stress_action_accepts_runtime_options() {
        let action = parse_action(&[
            "ares".to_string(),
            "stress".to_string(),
            "--requests".to_string(),
            "4".to_string(),
            "--concurrency".to_string(),
            "2".to_string(),
            "--prompt".to_string(),
            "safe check".to_string(),
        ]);

        assert_eq!(
            action,
            CliAction::Stress(StressArgs {
                requests: 4,
                concurrency: 2,
                prompt: "safe check".to_string(),
                python_executable: "endi/.venv/bin/python".to_string(),
                working_directory: "endi".to_string(),
                timeout_seconds: 60,
                provider: "ollama".to_string(),
                model: "granite4.1:3b".to_string(),
                base_url: "http://localhost:11434".to_string(),
            })
        );
    }
}
