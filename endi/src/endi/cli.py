"""CLI entrypoint for ENDI."""

import inspect
import json
from collections.abc import Mapping

import typer
from prompt_toolkit import prompt
from rich.console import Console

from endi import __version__
from endi.plugins import discover_plugin_commands
from endi.presentation import (
    TerminalProfile,
    build_confirmation_summary_panel,
    build_error_panel,
    build_help_panel,
    build_introspection_panel,
    build_result_panel,
    build_warning_panel,
    resolve_terminal_profile,
)
from endi.providers import (
    ProviderAdapterError,
    ProviderCapability,
    build_chat_provider,
    evaluate_local_fallback_policy,
    extract_chat_response_text,
    resolve_chat_provider_config,
)
from endi.routing import (
    DispatchResult,
    RouteKind,
    command_discoverability_catalog,
    dispatch_input,
)
from endi.runtime_logging import write_json_event

app = typer.Typer(help="ENDI terminal assistant")
_console = Console()


@app.callback()
def root() -> None:
    """ENDI command root."""


@app.command()
def version() -> None:
    """Print the ENDI version."""
    _console.print(f"ENDI {__version__}")


def _execute_command(command_name: str, command_args: list[str]) -> str:
    """Placeholder command execution path for slash-prefixed input."""
    if command_name in {"help", "introspect"}:
        del command_args
        return command_name

    suffix = f" {' '.join(command_args)}" if command_args else ""
    return f"[command] /{command_name}{suffix}"


def _discoverability_commands(plugin_dir: str | None = None) -> tuple[dict[str, object], ...]:
    commands = list(command_discoverability_catalog())
    plugin_result = discover_plugin_commands(plugin_dir)
    commands.extend(plugin_result.commands)
    return tuple(
        {
            "name": command.name,
            "description": command.description,
            "arg_schema": command.arg_schema,
            "examples": list(command.examples),
            "execution_target": command.execution_target,
        }
        for command in sorted(commands, key=lambda command: command.name)
    )


def _provider_context(
    *,
    provider: str | None,
    model: str | None,
    base_url: str | None,
    api_key_env: str | None,
    timeout_seconds: float,
    local_fallback: bool,
) -> dict[str, object]:
    context: dict[str, object] = {
        "chat_timeout_seconds": timeout_seconds,
        "provider_local_fallback_enabled": local_fallback,
    }
    if provider:
        context["chat_provider"] = provider
        context["provider_defaults"] = {"chat": provider}
    if model:
        context["chat_model"] = model
    if base_url:
        context["chat_base_url"] = base_url
    if api_key_env:
        context["chat_api_key_env"] = api_key_env
    return context


def _handle_conversation(text: str, *, context: Mapping[str, object] | None = None) -> str:
    """Generate a provider-backed response for free-text input."""
    messages: list[dict[str, object]] = [{"role": "user", "content": text}]
    provider_config = resolve_chat_provider_config(context)
    provider = build_chat_provider(provider_config)
    try:
        return extract_chat_response_text(provider.generate_reply(messages, context=context))
    except ProviderAdapterError as exc:
        fallback_decision = evaluate_local_fallback_policy(
            capability=ProviderCapability.CHAT,
            selected_provider=provider_config.identifier,
            failure_reason=exc.code,
            context=context,
        )
        if fallback_decision.error is None:
            fallback_provider = build_chat_provider(
                resolve_chat_provider_config(
                    {
                        **dict(context or {}),
                        "chat_provider": "ollama:llama3.1",
                        "provider_defaults": {"chat": "ollama:llama3.1"},
                    }
                )
            )
            return extract_chat_response_text(
                fallback_provider.generate_reply(messages, context=context)
            )
        return f"Provider error ({exc.code}): {exc}"


def _terminal_profile() -> TerminalProfile:
    return resolve_terminal_profile(_console.color_system)


def _extract_confirmation_summary(result: object) -> Mapping[str, object] | None:
    runtime_error = getattr(result, "runtime_error", None)
    if runtime_error is None:
        return None

    details = runtime_error.details
    if not isinstance(details, dict):
        return None

    summary = details.get("summary")
    if not isinstance(summary, dict):
        return None
    return summary


def _resolved_command_name(result: object) -> str | None:
    resolved_context = getattr(result, "resolved_context", None)
    if not isinstance(resolved_context, dict):
        return None
    command_name = resolved_context.get("command_name")
    if isinstance(command_name, str) and command_name:
        return command_name
    return None


def _print_runtime_error_context(result: object, *, profile: TerminalProfile) -> None:
    runtime_error = getattr(result, "runtime_error", None)
    if runtime_error is None:
        return

    details = [
        f"code={runtime_error.code}",
        f"component={runtime_error.component.value}",
        f"status_code={runtime_error.status_code or 'n/a'}",
    ]
    _console.print(
        build_warning_panel(
            title="Runtime Context",
            message="Runtime error envelope attached.",
            details=details,
            profile=profile,
        )
    )
    runtime_details = runtime_error.details
    if not runtime_details:
        return

    execution_id = runtime_details.get("execution_id")
    tool_name = runtime_details.get("tool_name")
    if execution_id is not None:
        _console.print(
            build_warning_panel(
                title="Runtime Context",
                message=f"execution_id={execution_id}",
                profile=profile,
            )
        )
    if tool_name is not None:
        _console.print(
            build_warning_panel(
                title="Runtime Context",
                message=f"tool_name={tool_name}",
                profile=profile,
            )
        )


def _result_envelope(result: object) -> dict[str, object]:
    route = getattr(result, "route", None)
    route_value = getattr(route, "value", str(route))
    envelope: dict[str, object] = {
        "route": route_value,
        "output": getattr(result, "output", None),
        "status": "error" if getattr(result, "runtime_error", None) is not None else "success",
    }
    validation_error = getattr(result, "validation_error", None)
    if validation_error is not None:
        envelope["validation_error"] = {
            "code": validation_error.code,
            "message": validation_error.message,
            "hint": validation_error.hint,
            "execution_id": validation_error.execution_id,
        }
    execution_error = getattr(result, "execution_error", None)
    if execution_error is not None:
        envelope["execution_error"] = {
            "component": execution_error.component.value,
            "failure_type": execution_error.failure_type,
            "message": execution_error.message,
            "execution_id": execution_error.execution_id,
        }
    runtime_error = getattr(result, "runtime_error", None)
    if runtime_error is not None:
        envelope["runtime_error"] = {
            "code": runtime_error.code,
            "component": runtime_error.component.value,
            "message": runtime_error.message,
            "status_code": runtime_error.status_code,
        }
    telemetry_payload = getattr(result, "telemetry_payload", None)
    if isinstance(telemetry_payload, dict):
        envelope["telemetry"] = telemetry_payload
    return envelope


def _print_json(result: object) -> None:
    _console.print(json.dumps(_result_envelope(result), sort_keys=True))


def _dispatch_input_with_context(
    submitted_input: str,
    provider_context: Mapping[str, object],
    explicit_context: dict[str, object],
) -> DispatchResult:
    dispatch_signature = inspect.signature(dispatch_input)
    supports_explicit_context = (
        "explicit_context" in dispatch_signature.parameters
        or any(
            parameter.kind is inspect.Parameter.VAR_KEYWORD
            for parameter in dispatch_signature.parameters.values()
        )
    )
    if supports_explicit_context:
        return dispatch_input(
            submitted_input,
            _execute_command,
            lambda text: _handle_conversation(text, context=provider_context),
            explicit_context=explicit_context,
        )
    return dispatch_input(
        submitted_input,
        _execute_command,
        lambda text: _handle_conversation(text, context=provider_context),
    )


def _dispatch_submit(
    submitted_input: str,
    *,
    output: str,
    provider: str | None,
    model: str | None,
    base_url: str | None,
    api_key_env: str | None,
    timeout_seconds: float,
    local_fallback: bool,
    approve_plan: bool,
    non_interactive: bool,
    log_json: str | None,
    plugin_dir: str | None,
) -> None:
    provider_context = _provider_context(
        provider=provider,
        model=model,
        base_url=base_url,
        api_key_env=api_key_env,
        timeout_seconds=timeout_seconds,
        local_fallback=local_fallback,
    )
    explicit_context = {
        **provider_context,
        "confirmation_mode": "approve_plan" if approve_plan else "per_action",
        "non_interactive": non_interactive,
    }
    result = _dispatch_input_with_context(
        submitted_input,
        provider_context,
        explicit_context,
    )
    write_json_event(
        log_json,
        {
            "route": result.route.value,
            "status": "error" if result.runtime_error is not None else "success",
            "output_present": result.output is not None,
            "telemetry": result.telemetry_payload or {},
        },
    )
    profile = _terminal_profile()
    command_name = _resolved_command_name(result)

    if output == "json":
        _print_json(result)
        if result.route in {RouteKind.VALIDATION_ERROR, RouteKind.EXECUTION_ERROR}:
            raise typer.Exit(code=1)
        return

    if result.route is RouteKind.VALIDATION_ERROR:
        validation_error = result.validation_error
        assert validation_error is not None
        confirmation_summary = _extract_confirmation_summary(result)
        if confirmation_summary is not None:
            _console.print(
                build_confirmation_summary_panel(summary=confirmation_summary, profile=profile)
            )
        details = [f"Hint: {validation_error.hint}"]
        if validation_error.execution_id:
            details.append(f"Execution ID: {validation_error.execution_id}")
        _console.print(
            build_error_panel(
                title="Validation Error",
                message=validation_error.message,
                details=details,
                profile=profile,
            )
        )
        _print_runtime_error_context(result, profile=profile)
        raise typer.Exit(code=1)

    if result.route is RouteKind.EXECUTION_ERROR:
        execution_error = result.execution_error
        assert execution_error is not None
        confirmation_summary = _extract_confirmation_summary(result)
        if confirmation_summary is not None:
            _console.print(
                build_confirmation_summary_panel(summary=confirmation_summary, profile=profile)
            )
        _console.print(
            build_error_panel(
                title="Execution Error",
                message=execution_error.message,
                details=(
                    f"Component: {execution_error.component}",
                    f"Failure type: {execution_error.failure_type}",
                    f"Execution ID: {execution_error.execution_id}",
                ),
                profile=profile,
            )
        )
        _print_runtime_error_context(result, profile=profile)
        raise typer.Exit(code=1)

    if result.route is RouteKind.COMMAND and command_name == "help":
        _console.print(
            build_help_panel(
                commands=_discoverability_commands(plugin_dir),
                profile=profile,
            )
        )
        return

    if result.route is RouteKind.COMMAND and command_name == "introspect":
        _console.print(
            build_introspection_panel(
                commands=_discoverability_commands(plugin_dir),
                profile=profile,
            )
        )
        return

    _console.print(
        build_result_panel(
            message=str(result.output),
            details=(f"Route: {result.route.value}",),
            profile=profile,
        )
    )


@app.command("submit")
def submit(
    input_text: str | None = typer.Argument(None),
    output: str = typer.Option("rich", "--output", help="Output format: rich or json."),
    provider: str | None = typer.Option(None, "--provider", help="Chat provider identifier."),
    model: str | None = typer.Option(None, "--model", help="Chat model override."),
    base_url: str | None = typer.Option(None, "--base-url", help="Provider base URL override."),
    api_key_env: str | None = typer.Option(None, "--api-key-env", help="Provider API key env var."),
    timeout_seconds: float = typer.Option(30.0, "--timeout-seconds", help="Provider timeout."),
    local_fallback: bool = typer.Option(False, "--local-fallback", help="Enable Ollama fallback."),
    approve_plan: bool = typer.Option(False, "--approve-plan", help="Use approve-plan mode."),
    non_interactive: bool = typer.Option(False, "--non-interactive", help="Disable prompts."),
    log_json: str | None = typer.Option(None, "--log-json", help="Append JSON log events to path."),
    plugin_dir: str | None = typer.Option(
        None,
        "--plugin-dir",
        help="Directory of plugin manifests.",
    ),
) -> None:
    """Submit one prompt and route it to command or conversation execution."""
    submitted_input = input_text if input_text is not None else prompt("> ")
    if output not in {"rich", "json"}:
        raise typer.BadParameter("output must be 'rich' or 'json'.")
    _dispatch_submit(
        submitted_input,
        output=output,
        provider=provider,
        model=model,
        base_url=base_url,
        api_key_env=api_key_env,
        timeout_seconds=timeout_seconds,
        local_fallback=local_fallback,
        approve_plan=approve_plan,
        non_interactive=non_interactive,
        log_json=log_json,
        plugin_dir=plugin_dir,
    )


@app.command("shell")
def shell(
    output: str = typer.Option("rich", "--output", help="Output format: rich or json."),
    provider: str | None = typer.Option(None, "--provider", help="Chat provider identifier."),
    model: str | None = typer.Option(None, "--model", help="Chat model override."),
    base_url: str | None = typer.Option(None, "--base-url", help="Provider base URL override."),
    plugin_dir: str | None = typer.Option(
        None,
        "--plugin-dir",
        help="Directory of plugin manifests.",
    ),
) -> None:
    """Run an interactive ENDI shell until /exit or /quit."""
    while True:
        try:
            submitted_input = prompt("> ")
        except EOFError:
            return
        if submitted_input.strip() in {"/exit", "/quit"}:
            return
        if not submitted_input.strip():
            continue
        _dispatch_submit(
            submitted_input,
            output=output,
            provider=provider,
            model=model,
            base_url=base_url,
            api_key_env=None,
            timeout_seconds=30.0,
            local_fallback=False,
            approve_plan=False,
            non_interactive=False,
            log_json=None,
            plugin_dir=plugin_dir,
        )


def main() -> None:
    """Run the ENDI CLI app."""
    app()


if __name__ == "__main__":
    main()
