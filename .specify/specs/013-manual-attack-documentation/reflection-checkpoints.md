# Reflection Checkpoints

## Reflection 1: After Manual Attacks

AI tools helped generate safe, categorized attack prompts and keep the evidence
table aligned with the BA/PM rubric. The risky assumption was that local Ollama
would be running at `http://localhost:11434`; it was not available in this
session, so all five manual attempts produced real ENDI provider-connection
errors instead of model behavior. Manual testing still found an operational
issue: ENDI tries to persist provider defaults under the user config directory
unless `ENDI_CONFIG_PATH` is set, which can fail in sandboxed environments.

## Reflection 2: After Mitigation Replay

The ENDI target policy mitigation has been implemented, but replay against a
live model could not prove behavioral risk reduction because local Ollama was
unavailable during this evidence pass. The next replay should start Ollama,
confirm `granite4.1:3b` is installed, run the same attacks with
`--system-prompt-file endi/config/target_policy.md`, and compare baseline vs.
mitigated classifications by stable attack ID.
