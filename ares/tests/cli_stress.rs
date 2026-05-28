use std::fs;
use std::process::Command;

#[test]
fn cli_stress_runs_endi_contract_and_prints_summary() {
    let temp_dir = std::env::temp_dir().join(format!("ares-cli-stress-{}", std::process::id()));
    fs::create_dir_all(&temp_dir).expect("temp dir");
    let fake_endi = temp_dir.join("fake-endi");
    fs::write(
        &fake_endi,
        "#!/usr/bin/env sh\nprintf '{\"route\":\"conversation\",\"output\":\"ok\",\"status\":\"ok\"}'\n",
    )
    .expect("fake endi");
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let mut permissions = fs::metadata(&fake_endi).expect("metadata").permissions();
        permissions.set_mode(0o755);
        fs::set_permissions(&fake_endi, permissions).expect("permissions");
    }

    let output = Command::new(env!("CARGO_BIN_EXE_ares"))
        .args([
            "stress",
            "--requests",
            "2",
            "--concurrency",
            "1",
            "--prompt",
            "safe health check",
            "--python-executable",
            fake_endi.to_str().expect("utf8 path"),
            "--working-directory",
            temp_dir.to_str().expect("utf8 path"),
        ])
        .output()
        .expect("run ares stress");

    assert!(
        output.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    let stdout = String::from_utf8_lossy(&output.stdout);
    assert!(stdout.contains("ARES stress summary"));
    assert!(stdout.contains("Total requests: 2"));
    assert!(stdout.contains("Success: 2"));
}
