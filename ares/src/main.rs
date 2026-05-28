use anyhow::Result;
use ares::attacks::fixture::load_attack_fixtures;
use ares::cli::{CliAction, HELP_TEXT, parse_action};
use ares::config::{AresConfig, CliConfigOverrides};
use ares::evaluator::{EvidenceRecord, evaluate};
use ares::reporting::{Report, ReportArtifactStatus, ReportFinding, write_markdown_report};
use ares::runner::{AttackRunner, RunConfig};
use ares::stress::{StressRunConfig, run_stress};
use ares::targets::endi::{EndiClient, EndiExecutionConfig};
use std::path::PathBuf;
use std::time::Duration;
use tracing::info;
use tracing_subscriber::EnvFilter;

fn main() -> Result<()> {
    init_tracing();
    let args: Vec<String> = std::env::args().collect();
    match parse_action(&args) {
        CliAction::Help => print!("{HELP_TEXT}"),
        CliAction::Version => println!("ares {}", env!("CARGO_PKG_VERSION")),
        CliAction::Run(args) => {
            let config = load_run_config(&args)?;
            let fixture = args
                .fixture
                .clone()
                .unwrap_or_else(|| config.runtime.attack_fixture.clone());
            let report_path = args
                .report
                .clone()
                .unwrap_or_else(|| config.runtime.report_path.clone());
            info!(command = "run", fixture = %fixture, "starting attack run");
            let attacks = load_attack_fixtures(&PathBuf::from(&fixture))?;
            let run_id = ares::attacks::domain::RunId::new(
                args.run_id.clone().unwrap_or_else(generate_cli_run_id),
            )?;
            let client = EndiClient::new(EndiExecutionConfig {
                python_executable: PathBuf::from(config.endi.command.python_executable),
                working_directory: PathBuf::from(config.endi.command.working_directory),
                timeout: Duration::from_secs(config.endi.command.timeout_seconds),
                provider: config.endi.target.provider,
                model: config.endi.target.model,
                base_url: config.endi.target.base_url,
                ..EndiExecutionConfig::default()
            });
            let run = AttackRunner::new(client).run_bounded(
                attacks,
                RunConfig {
                    run_id: run_id.clone(),
                    max_concurrency: config.runtime.max_concurrency,
                },
            );
            let findings = run
                .results
                .iter()
                .map(|result| {
                    let evidence = EvidenceRecord::from_run_result(result, true);
                    let decision = evaluate(&evidence);
                    ReportFinding { evidence, decision }
                })
                .collect();
            let report = Report {
                title: "ARES Vulnerability Report".to_string(),
                run_id: run_id.as_str().to_string(),
                findings,
                manual_attacks: ReportArtifactStatus::new(
                    ".specify/specs/013-manual-attack-documentation/manual-attacks.md",
                    true,
                ),
                reflections: ReportArtifactStatus::new(
                    ".specify/specs/013-manual-attack-documentation/reflection-checkpoints.md",
                    true,
                ),
                replay: Vec::new(),
            };
            write_markdown_report(&report, &PathBuf::from(&report_path))?;
            println!("ARES run complete");
            println!("Attacks: {}", run.results.len());
            println!("Report: {report_path}");
        }
        CliAction::Stress(args) => {
            info!(command = "stress", "starting stress command");
            let config = StressRunConfig::new(args.requests, args.concurrency)?;
            let client = EndiClient::new(EndiExecutionConfig {
                python_executable: PathBuf::from(args.python_executable),
                working_directory: PathBuf::from(args.working_directory),
                timeout: Duration::from_secs(args.timeout_seconds),
                provider: args.provider,
                model: args.model,
                base_url: args.base_url,
                ..EndiExecutionConfig::default()
            });
            let summary = run_stress(client, &args.prompt, config);
            println!("ARES stress summary");
            println!("Total requests: {}", summary.total);
            println!("Success: {}", summary.success_count);
            println!("Target errors: {}", summary.target_error_count);
            println!("Harness errors: {}", summary.harness_error_count);
            println!("Timeouts: {}", summary.timeout_count);
            println!("Non-zero exits: {}", summary.non_zero_exit_count);
            println!("Max latency ms: {}", summary.max_latency_ms);
        }
    }
    Ok(())
}

fn load_run_config(args: &ares::cli::RunArgs) -> Result<AresConfig> {
    let config = match args.config.as_deref() {
        Some(path) => AresConfig::load_from_file(&PathBuf::from(path))?,
        None => AresConfig::default(),
    };
    Ok(config.with_overrides(CliConfigOverrides {
        provider: args.provider.clone(),
        model: args.model.clone(),
        base_url: args.base_url.clone(),
        timeout_seconds: args.timeout_seconds,
        output_directory: None,
        attack_fixture: args.fixture.clone(),
        report_path: args.report.clone(),
        python_executable: args.python_executable.clone(),
        working_directory: args.working_directory.clone(),
        max_concurrency: args.concurrency,
    }))
}

fn generate_cli_run_id() -> String {
    let epoch_ms = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|duration| duration.as_millis())
        .unwrap_or(0);
    format!("run-{epoch_ms}")
}

fn init_tracing() {
    let _ = tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::from_default_env())
        .try_init();
}
