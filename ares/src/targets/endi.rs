use std::fmt;
use std::path::PathBuf;
use std::process::{Command, Stdio};
use std::thread;
use std::time::{Duration, Instant, SystemTime};

#[derive(Debug, Clone)]
pub struct EndiExecutionConfig {
    pub python_executable: PathBuf,
    pub module: String,
    pub working_directory: PathBuf,
    pub timeout: Duration,
    pub provider: String,
    pub model: String,
    pub base_url: String,
}

impl Default for EndiExecutionConfig {
    fn default() -> Self {
        Self {
            python_executable: PathBuf::from("endi/.venv/bin/python"),
            module: "endi.cli".to_string(),
            working_directory: PathBuf::from("endi"),
            timeout: Duration::from_secs(60),
            provider: "ollama".to_string(),
            model: "granite4.1:3b".to_string(),
            base_url: "http://localhost:11434".to_string(),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ParsedEndiOutput {
    pub route: String,
    pub output: Option<String>,
    pub status: String,
}

#[derive(Debug, Clone)]
pub struct EndiCommandResult {
    pub command: String,
    pub stdout: String,
    pub stderr: String,
    pub exit_code: Option<i32>,
    pub started_at: SystemTime,
    pub duration_ms: u128,
    pub timed_out: bool,
    pub parsed_output: Option<ParsedEndiOutput>,
}

#[derive(Debug)]
pub struct EndiCommandError {
    message: String,
}

impl EndiCommandError {
    fn new(message: impl Into<String>) -> Self {
        Self {
            message: message.into(),
        }
    }

    pub fn new_for_test(message: impl Into<String>) -> Self {
        Self::new(message)
    }
}

impl fmt::Display for EndiCommandError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str(&self.message)
    }
}

impl std::error::Error for EndiCommandError {}

#[derive(Debug, Clone)]
pub struct EndiEnvironmentStatus {
    pub python_exists: bool,
    pub working_directory_exists: bool,
}

#[derive(Debug, Clone)]
pub struct EndiClient {
    config: EndiExecutionConfig,
}

impl EndiClient {
    pub fn new(config: EndiExecutionConfig) -> Self {
        Self { config }
    }

    pub fn version(&self) -> Result<EndiCommandResult, EndiCommandError> {
        self.run(vec!["--version".to_string()])
    }

    pub fn chat(&self, prompt: &str) -> Result<EndiCommandResult, EndiCommandError> {
        self.run(self.prompt_args("chat", prompt))
    }

    pub fn submit(&self, prompt: &str) -> Result<EndiCommandResult, EndiCommandError> {
        self.run(self.prompt_args("submit", prompt))
    }

    pub fn validate_environment(&self) -> EndiEnvironmentStatus {
        EndiEnvironmentStatus {
            python_exists: self.config.python_executable.exists(),
            working_directory_exists: self.config.working_directory.exists(),
        }
    }

    fn prompt_args(&self, command: &str, prompt: &str) -> Vec<String> {
        vec![
            "-m".to_string(),
            self.config.module.clone(),
            command.to_string(),
            prompt.to_string(),
            "--provider".to_string(),
            self.config.provider.clone(),
            "--model".to_string(),
            self.config.model.clone(),
            "--base-url".to_string(),
            self.config.base_url.clone(),
            "--timeout-seconds".to_string(),
            self.config.timeout.as_secs().to_string(),
            "--output".to_string(),
            "json".to_string(),
            "--non-interactive".to_string(),
        ]
    }

    fn run(&self, args: Vec<String>) -> Result<EndiCommandResult, EndiCommandError> {
        let started_at = SystemTime::now();
        let started = Instant::now();
        let command_string = command_string(&self.config.python_executable, &args);
        let mut child = Command::new(&self.config.python_executable)
            .args(&args)
            .current_dir(&self.config.working_directory)
            .stdin(Stdio::null())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .map_err(|error| {
                EndiCommandError::new(format!("failed to start ENDI command: {error}"))
            })?;

        loop {
            if child
                .try_wait()
                .map_err(|error| {
                    EndiCommandError::new(format!("failed to wait for ENDI: {error}"))
                })?
                .is_some()
            {
                let output = child.wait_with_output().map_err(|error| {
                    EndiCommandError::new(format!("failed to collect ENDI output: {error}"))
                })?;
                let stdout = String::from_utf8_lossy(&output.stdout).to_string();
                return Ok(EndiCommandResult {
                    command: command_string,
                    stderr: String::from_utf8_lossy(&output.stderr).to_string(),
                    exit_code: output.status.code(),
                    parsed_output: parse_endi_output(&stdout),
                    stdout,
                    started_at,
                    duration_ms: started.elapsed().as_millis().max(1),
                    timed_out: false,
                });
            }
            if started.elapsed() >= self.config.timeout {
                let _ = child.kill();
                let _ = child.wait();
                return Ok(EndiCommandResult {
                    command: command_string,
                    stdout: String::new(),
                    stderr: String::new(),
                    exit_code: None,
                    started_at,
                    duration_ms: started.elapsed().as_millis().max(1),
                    timed_out: true,
                    parsed_output: None,
                });
            }
            thread::sleep(Duration::from_millis(5));
        }
    }
}

fn command_string(program: &std::path::Path, args: &[String]) -> String {
    let mut parts = vec![program.display().to_string()];
    parts.extend(args.iter().cloned());
    parts.join(" ")
}

fn parse_endi_output(stdout: &str) -> Option<ParsedEndiOutput> {
    Some(ParsedEndiOutput {
        route: extract_json_string(stdout, "route")?,
        output: extract_json_string(stdout, "output"),
        status: extract_json_string(stdout, "status")?,
    })
}

fn extract_json_string(input: &str, key: &str) -> Option<String> {
    let needle = format!("\"{key}\":\"");
    let start = input.find(&needle)? + needle.len();
    let tail = &input[start..];
    let end = tail.find('"')?;
    Some(tail[..end].to_string())
}
