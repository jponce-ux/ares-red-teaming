use std::fs;
use std::path::PathBuf;
use std::time::Duration;

use ares::targets::endi::{EndiClient, EndiExecutionConfig};

fn fake_endi_script(name: &str, body: &str) -> PathBuf {
    let dir = std::env::temp_dir().join(format!("ares-endi-test-{}-{}", name, std::process::id()));
    fs::create_dir_all(&dir).expect("temp dir");
    let path = dir.join("fake_endi.sh");
    fs::write(&path, body).expect("fake script");
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let mut perms = fs::metadata(&path).expect("metadata").permissions();
        perms.set_mode(0o755);
        fs::set_permissions(&path, perms).expect("permissions");
    }
    path
}

#[test]
fn chat_executes_endi_cli_and_captures_json_output() {
    let script = fake_endi_script(
        "success",
        r#"#!/usr/bin/env bash
printf '{"route":"conversation","output":"hello from endi","status":"success"}'
"#,
    );
    let client = EndiClient::new(EndiExecutionConfig {
        python_executable: script,
        module: "endi.cli".to_string(),
        working_directory: std::env::temp_dir(),
        timeout: Duration::from_secs(2),
        provider: "ollama".to_string(),
        model: "granite4.1:3b".to_string(),
        base_url: "http://localhost:11434".to_string(),
    });

    let result = client.chat("hello").expect("chat result");

    assert_eq!(result.exit_code, Some(0));
    assert!(!result.timed_out);
    assert_eq!(
        result.parsed_output.as_ref().expect("parsed").route,
        "conversation"
    );
    assert_eq!(
        result.parsed_output.as_ref().expect("parsed").status,
        "success"
    );
    assert!(result.command.contains("--provider ollama"));
    assert!(result.command.contains("--model granite4.1:3b"));
    assert!(result.duration_ms > 0);
}

#[test]
fn adapter_reports_missing_command() {
    let client = EndiClient::new(EndiExecutionConfig {
        python_executable: PathBuf::from("/definitely/missing/endi-python"),
        ..EndiExecutionConfig::default()
    });

    let error = client.version().expect_err("missing command error");

    assert!(error.to_string().contains("failed to start ENDI"));
}

#[test]
fn adapter_reports_non_zero_exit() {
    let script = fake_endi_script(
        "nonzero",
        r#"#!/usr/bin/env bash
printf 'bad'
exit 7
"#,
    );
    let client = EndiClient::new(EndiExecutionConfig {
        python_executable: script,
        working_directory: std::env::temp_dir(),
        timeout: Duration::from_secs(2),
        ..EndiExecutionConfig::default()
    });

    let result = client.submit("hello").expect("non-zero captured");

    assert_eq!(result.exit_code, Some(7));
    assert_eq!(result.stdout, "bad");
}

#[test]
fn adapter_times_out_long_running_command() {
    let script = fake_endi_script(
        "timeout",
        r#"#!/usr/bin/env bash
sleep 3
"#,
    );
    let client = EndiClient::new(EndiExecutionConfig {
        python_executable: script,
        working_directory: std::env::temp_dir(),
        timeout: Duration::from_millis(50),
        ..EndiExecutionConfig::default()
    });

    let result = client.chat("hello").expect("timeout captured");

    assert!(result.timed_out);
    assert_eq!(result.exit_code, None);
}
