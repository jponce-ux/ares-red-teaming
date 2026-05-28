use std::collections::BTreeMap;

pub const REDACTED: &str = "***REDACTED***";

pub fn redact_sensitive_fields(fields: Vec<(String, String)>) -> BTreeMap<String, String> {
    fields
        .into_iter()
        .map(|(key, value)| {
            let redacted = if is_sensitive_key(&key) {
                REDACTED.to_string()
            } else {
                value
            };
            (key, redacted)
        })
        .collect()
}

fn is_sensitive_key(key: &str) -> bool {
    matches!(
        key.trim().to_ascii_lowercase().as_str(),
        "prompt" | "response" | "raw_prompt" | "raw_response" | "secret" | "token" | "api_key"
    )
}
