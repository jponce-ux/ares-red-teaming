use ares::cli::{CliAction, HELP_TEXT, parse_action};

fn main() {
    let args: Vec<String> = std::env::args().collect();
    match parse_action(&args) {
        CliAction::Help => print!("{HELP_TEXT}"),
        CliAction::Version => println!("ares {}", env!("CARGO_PKG_VERSION")),
        CliAction::Stress => println!("ARES stress mode"),
    }
}
