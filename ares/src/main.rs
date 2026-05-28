use anyhow::Result;
use ares::cli::{CliAction, HELP_TEXT, parse_action};
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

fn init_tracing() {
    let _ = tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::from_default_env())
        .try_init();
}
