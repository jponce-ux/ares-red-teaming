use ares::observability::{
    ObservabilityConfig, RunId, StructuredEvent, redact_sensitive_fields, structured_event,
};

#[test]
fn run_id_generation_and_parsing_are_stable() {
    let generated = RunId::generate();
    let parsed = RunId::parse("run-custom").expect("run id");

    assert!(generated.as_str().starts_with("run-"));
    assert_eq!(parsed.as_str(), "run-custom");
    assert!(RunId::parse("").is_err());
}

#[test]
fn redaction_removes_raw_prompt_and_response_fields() {
    let fields = vec![
        ("run_id".to_string(), "run-1".to_string()),
        ("prompt".to_string(), "secret prompt".to_string()),
        ("response".to_string(), "secret response".to_string()),
    ];

    let redacted = redact_sensitive_fields(fields);

    assert_eq!(redacted.get("run_id").map(String::as_str), Some("run-1"));
    assert_eq!(
        redacted.get("prompt").map(String::as_str),
        Some("***REDACTED***")
    );
    assert_eq!(
        redacted.get("response").map(String::as_str),
        Some("***REDACTED***")
    );
}

#[test]
fn structured_event_contains_stage_and_safe_metadata() {
    let event: StructuredEvent = structured_event(
        "attack",
        RunId::parse("run-1").expect("run id"),
        vec![("prompt".to_string(), "do not leak".to_string())],
        ObservabilityConfig::default(),
    );

    assert_eq!(event.stage, "attack");
    assert_eq!(event.run_id.as_str(), "run-1");
    assert_eq!(
        event.fields.get("prompt").map(String::as_str),
        Some("***REDACTED***")
    );
}
