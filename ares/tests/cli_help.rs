use std::process::Command;

#[test]
fn cli_help_shows_ares_entrypoint() {
    let output = Command::new(env!("CARGO_BIN_EXE_ares"))
        .arg("--help")
        .output()
        .expect("ares binary runs");

    assert!(output.status.success());
    let stdout = String::from_utf8(output.stdout).expect("stdout is UTF-8");
    assert!(stdout.contains("ARES"));
    assert!(stdout.contains("red-team"));
    assert!(stdout.contains("Usage:"));
}
