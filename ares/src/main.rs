use anyhow::Result;
use ares::cli::{CliAction, HELP_TEXT, parse_action};
use tracing::info;
use tracing_subscriber::EnvFilter;

fn main() -> Result<()> {
    init_tracing();
    let args: Vec<String> = std::env::args().collect();
    match parse_action(&args) {
        CliAction::Help => print!("{HELP_TEXT}"),
        CliAction::Version => println!("ares {}", env!("CARGO_PKG_VERSION")),
        CliAction::Stress => {
            info!(command = "stress", "starting stress command");
            println!("ARES stress mode");
        }
    }
    Ok(())
}

fn init_tracing() {
    let _ = tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::from_default_env())
        .try_init();
}
