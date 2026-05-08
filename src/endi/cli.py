"""CLI entrypoint for ENDI."""

from collections.abc import Mapping

import typer
from prompt_toolkit import prompt
from rich.console import Console

from endi import __version__
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
from endi.routing import RouteKind, command_discoverability_catalog, dispatch_input

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


def _discoverability_commands() -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "name": command.name,
            "description": command.description,
            "arg_schema": command.arg_schema,
            "examples": list(command.examples),
            "execution_target": command.execution_target,
        }
        for command in command_discoverability_catalog()
    )


def _handle_conversation(text: str) -> str:
    """Placeholder conversational path for free-text input."""
    return f"[conversation] {text}"


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


@app.command("submit")
def submit(input_text: str | None = typer.Argument(None)) -> None:
    """Submit one prompt and route it to command or conversation execution."""
    submitted_input = input_text if input_text is not None else prompt("> ")
    result = dispatch_input(submitted_input, _execute_command, _handle_conversation)
    profile = _terminal_profile()
    command_name = _resolved_command_name(result)

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
                commands=_discoverability_commands(),
                profile=profile,
            )
        )
        return

    if result.route is RouteKind.COMMAND and command_name == "introspect":
        _console.print(
            build_introspection_panel(
                commands=_discoverability_commands(),
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


def main() -> None:
    """Run the ENDI CLI app."""
    app()


if __name__ == "__main__":
    main()
