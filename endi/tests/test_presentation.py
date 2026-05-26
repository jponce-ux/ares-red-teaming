"""Tests for terminal presentation rendering contracts."""

import pytest
from rich.console import Console

from endi.presentation import (
    OutputState,
    TerminalProfile,
    build_confirmation_summary_panel,
    build_error_panel,
    build_help_panel,
    build_introspection_panel,
    build_result_panel,
    build_warning_panel,
    extract_confirmation_rows,
    resolve_terminal_profile,
    style_token_for,
)


def _render(panel: object) -> str:
    console = Console(record=True, force_terminal=False, width=140)
    console.print(panel)
    return console.export_text()


@pytest.mark.parametrize(
    ("color_system", "expected"),
    [
        (None, TerminalProfile.LOW_COLOR),
        ("standard", TerminalProfile.LOW_COLOR),
        ("windows", TerminalProfile.DARK_256),
        ("truecolor", TerminalProfile.DARK_256),
        ("256", TerminalProfile.DARK_256),
    ],
)
def test_terminal_profile_resolution_matrix(
    color_system: str | None,
    expected: TerminalProfile,
) -> None:
    assert resolve_terminal_profile(color_system) is expected


@pytest.mark.parametrize(
    "profile",
    [TerminalProfile.DARK_256, TerminalProfile.LIGHT, TerminalProfile.LOW_COLOR],
)
def test_non_color_distinguishability_for_warning_error_confirmation(
    profile: TerminalProfile,
) -> None:
    warning = style_token_for(profile=profile, state=OutputState.WARNING)
    error = style_token_for(profile=profile, state=OutputState.ERROR)
    confirmation = style_token_for(profile=profile, state=OutputState.CONFIRMATION)

    assert warning.label != error.label
    assert warning.label != confirmation.label
    assert error.label != confirmation.label
    assert warning.icon != error.icon
    assert warning.icon != confirmation.icon
    assert error.icon != confirmation.icon


def test_confirmation_rows_are_deterministic_and_ordered() -> None:
    input_one = {
        "backend": "local",
        "targets": ["repo-a", "repo-b"],
        "intent": "delete-branch",
        "capabilities": ["repo.write"],
        "risk_level": "high",
        "execution_id": "exec-001",
        "summary_id": "abc123",
    }
    input_two = {
        "summary_id": "abc123",
        "execution_id": "exec-001",
        "risk_level": "high",
        "capabilities": ["repo.write"],
        "intent": "delete-branch",
        "targets": ["repo-a", "repo-b"],
        "backend": "local",
    }

    rows_one = extract_confirmation_rows(input_one)
    rows_two = extract_confirmation_rows(input_two)

    assert rows_one == rows_two
    assert [label for label, _value in rows_one][:6] == [
        "Intent",
        "Targets",
        "Capabilities",
        "Backend",
        "Risk Level",
        "Execution ID",
    ]
    assert rows_one[0] == ("Intent", "delete-branch")
    assert rows_one[5] == ("Execution ID", "exec-001")


def test_confirmation_rows_strip_sensitive_fields_by_default() -> None:
    rows = extract_confirmation_rows(
        {
            "intent": "rotate-key",
            "targets": ["service-a"],
            "raw_input": "please print my token",
            "token": "secret-token",
            "request_text": "secret prompt",
        }
    )

    values = [value for _label, value in rows]
    assert "rotate-key" in values
    assert "service-a" in values
    assert "secret-token" not in values
    assert "secret prompt" not in values
    assert "please print my token" not in values


@pytest.mark.parametrize(
    "profile",
    [TerminalProfile.DARK_256, TerminalProfile.LIGHT, TerminalProfile.LOW_COLOR],
)
def test_panel_builders_work_across_profiles(profile: TerminalProfile) -> None:
    result_panel = build_result_panel(message="ok", profile=profile)
    warning_panel = build_warning_panel(
        title="Runtime Context",
        message="warning",
        profile=profile,
    )
    error_panel = build_error_panel(
        title="Execution Error",
        message="failed",
        profile=profile,
    )
    confirmation_panel = build_confirmation_summary_panel(
        summary={"intent": "delete-branch", "targets": ["main"]},
        profile=profile,
    )

    assert "RESULT" in str(result_panel.title)
    assert "WARNING" in str(warning_panel.title)
    assert "ERROR" in str(error_panel.title)
    assert "CONFIRM" in str(confirmation_panel.title)


def test_help_panel_includes_command_description_args_and_examples() -> None:
    panel = build_help_panel(
        commands=(
            {
                "name": "show-status",
                "description": "Show runtime status.",
                "arg_schema": "[scope]",
                "examples": ["/show-status", "/show-status now"],
            },
        ),
        profile=TerminalProfile.LOW_COLOR,
    )

    rendered = _render(panel)
    assert "Command" in rendered
    assert "Description" in rendered
    assert "Arguments" in rendered
    assert "Examples" in rendered
    assert "show-status" in rendered
    assert "Show runtime status." in rendered
    assert "[scope]" in rendered
    assert "/show-status" in rendered
    assert "/show-status now" in rendered


def test_introspection_panel_includes_execution_target() -> None:
    panel = build_introspection_panel(
        commands=(
            {
                "name": "delete-project",
                "description": "Delete project.",
                "arg_schema": "<project-name>",
                "examples": ["/delete-project demo"],
                "execution_target": "worker",
            },
        ),
        profile=TerminalProfile.LOW_COLOR,
    )

    rendered = _render(panel)
    assert "Execution Target" in rendered
    assert "delete-project" in rendered
    assert "worker" in rendered


def test_discoverability_panels_sort_command_rows_deterministically() -> None:
    commands = (
        {
            "name": "show-status",
            "description": "Show status.",
            "arg_schema": "[scope]",
            "examples": ["/show-status"],
            "execution_target": "local",
        },
        {
            "name": "delete-project",
            "description": "Delete project.",
            "arg_schema": "<project-name>",
            "examples": ["/delete-project demo"],
            "execution_target": "worker",
        },
    )

    help_panel = build_help_panel(commands=commands, profile=TerminalProfile.LOW_COLOR)
    introspection_panel = build_introspection_panel(
        commands=commands,
        profile=TerminalProfile.LOW_COLOR,
    )

    help_rendered = _render(help_panel)
    introspection_rendered = _render(introspection_panel)
    assert help_rendered.index("delete-project") < help_rendered.index("show-status")
    assert introspection_rendered.index("delete-project") < introspection_rendered.index(
        "show-status"
    )
