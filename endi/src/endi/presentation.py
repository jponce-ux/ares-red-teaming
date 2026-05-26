"""Centralized Rich terminal presentation helpers for ENDI CLI surfaces."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Literal, overload

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from endi.context import is_sensitive_key


class TerminalProfile(StrEnum):
    """Supported terminal readability profiles."""

    DARK_256 = "dark_256"
    LIGHT = "light"
    LOW_COLOR = "low_color"


class OutputState(StrEnum):
    """Semantic output states for terminal rendering."""

    RESULT = "result"
    WARNING = "warning"
    ERROR = "error"
    CONFIRMATION = "confirmation"


@dataclass(frozen=True)
class StyleToken:
    """Deterministic style token bundle for a semantic output state."""

    label: str
    icon: str
    border_style: str
    title_style: str
    body_style: str


_STYLE_MATRIX: dict[TerminalProfile, dict[OutputState, StyleToken]] = {
    TerminalProfile.DARK_256: {
        OutputState.RESULT: StyleToken(
            label="RESULT",
            icon="✔",
            border_style="green",
            title_style="bold green",
            body_style="white",
        ),
        OutputState.WARNING: StyleToken(
            label="WARNING",
            icon="▲",
            border_style="yellow",
            title_style="bold yellow",
            body_style="white",
        ),
        OutputState.ERROR: StyleToken(
            label="ERROR",
            icon="✖",
            border_style="red",
            title_style="bold red",
            body_style="white",
        ),
        OutputState.CONFIRMATION: StyleToken(
            label="CONFIRM",
            icon="⚠",
            border_style="bright_magenta",
            title_style="bold bright_magenta",
            body_style="white",
        ),
    },
    TerminalProfile.LIGHT: {
        OutputState.RESULT: StyleToken(
            label="RESULT",
            icon="✔",
            border_style="dark_green",
            title_style="bold dark_green",
            body_style="black",
        ),
        OutputState.WARNING: StyleToken(
            label="WARNING",
            icon="▲",
            border_style="dark_orange",
            title_style="bold dark_orange",
            body_style="black",
        ),
        OutputState.ERROR: StyleToken(
            label="ERROR",
            icon="✖",
            border_style="dark_red",
            title_style="bold dark_red",
            body_style="black",
        ),
        OutputState.CONFIRMATION: StyleToken(
            label="CONFIRM",
            icon="⚠",
            border_style="purple4",
            title_style="bold purple4",
            body_style="black",
        ),
    },
    TerminalProfile.LOW_COLOR: {
        OutputState.RESULT: StyleToken(
            label="RESULT",
            icon="OK",
            border_style="none",
            title_style="bold",
            body_style="none",
        ),
        OutputState.WARNING: StyleToken(
            label="WARNING",
            icon="!!",
            border_style="none",
            title_style="bold",
            body_style="none",
        ),
        OutputState.ERROR: StyleToken(
            label="ERROR",
            icon="XX",
            border_style="none",
            title_style="bold",
            body_style="none",
        ),
        OutputState.CONFIRMATION: StyleToken(
            label="CONFIRM",
            icon="??",
            border_style="none",
            title_style="bold",
            body_style="none",
        ),
    },
}

_CONFIRMATION_FIELD_ORDER: tuple[str, ...] = (
    "intent",
    "targets",
    "capabilities",
    "backend",
    "risk_level",
    "execution_id",
    "summary_id",
    "plan_fingerprint",
    "action_count",
    "context_id",
)

_CONFIRMATION_FIELD_LABELS: dict[str, str] = {
    "intent": "Intent",
    "targets": "Targets",
    "capabilities": "Capabilities",
    "backend": "Backend",
    "risk_level": "Risk Level",
    "execution_id": "Execution ID",
    "summary_id": "Summary ID",
    "plan_fingerprint": "Plan Fingerprint",
    "action_count": "Action Count",
    "context_id": "Context ID",
}


def resolve_terminal_profile(color_system: str | None) -> TerminalProfile:
    """Resolve profile from console color capability."""
    if color_system in {None, "standard"}:
        return TerminalProfile.LOW_COLOR
    return TerminalProfile.DARK_256


def style_token_for(*, profile: TerminalProfile, state: OutputState) -> StyleToken:
    """Return centralized semantic style token for state/profile pair."""
    return _STYLE_MATRIX[profile][state]


def _panel_title(token: StyleToken, section_title: str) -> Text:
    return Text(
        f"{token.icon} [{token.label}] {section_title}",
        style=token.title_style,
    )


def _build_state_panel(
    *,
    state: OutputState,
    title: str,
    message: str,
    details: Sequence[str] = (),
    profile: TerminalProfile,
) -> Panel:
    token = style_token_for(profile=profile, state=state)
    lines = [Text(message, style=token.body_style)]
    for detail in details:
        lines.append(Text(detail, style=token.body_style))
    body = Group(*lines)
    return Panel(
        body,
        title=_panel_title(token, title),
        border_style=token.border_style,
        expand=False,
    )


def build_result_panel(
    *,
    message: str,
    details: Sequence[str] = (),
    profile: TerminalProfile,
) -> Panel:
    """Build deterministic result panel."""
    return _build_state_panel(
        state=OutputState.RESULT,
        title="Result",
        message=message,
        details=details,
        profile=profile,
    )


def build_warning_panel(
    *,
    title: str,
    message: str,
    details: Sequence[str] = (),
    profile: TerminalProfile,
) -> Panel:
    """Build deterministic warning panel."""
    return _build_state_panel(
        state=OutputState.WARNING,
        title=title,
        message=message,
        details=details,
        profile=profile,
    )


def build_error_panel(
    *,
    title: str,
    message: str,
    details: Sequence[str] = (),
    profile: TerminalProfile,
) -> Panel:
    """Build deterministic error panel."""
    return _build_state_panel(
        state=OutputState.ERROR,
        title=title,
        message=message,
        details=details,
        profile=profile,
    )


def _discoverability_value(value: object) -> str:
    if isinstance(value, str):
        return value
    return ""


def _discoverability_examples(value: object) -> str:
    if not isinstance(value, Sequence) or isinstance(value, str):
        return ""
    examples = [example for example in value if isinstance(example, str) and example]
    return " | ".join(examples)


@overload
def _discoverability_rows(
    commands: Sequence[Mapping[str, object]],
    *,
    include_target: Literal[False],
) -> tuple[tuple[str, str, str, str], ...]: ...


@overload
def _discoverability_rows(
    commands: Sequence[Mapping[str, object]],
    *,
    include_target: Literal[True],
) -> tuple[tuple[str, str, str, str, str], ...]: ...


def _discoverability_rows(
    commands: Sequence[Mapping[str, object]],
    *,
    include_target: bool,
) -> tuple[tuple[str, str, str, str] | tuple[str, str, str, str, str], ...]:
    rows: list[tuple[str, str, str, str] | tuple[str, str, str, str, str]] = []
    sorted_commands = sorted(
        commands,
        key=lambda command: _discoverability_value(command.get("name")),
    )
    for command in sorted_commands:
        name = _discoverability_value(command.get("name"))
        description = _discoverability_value(command.get("description"))
        arg_schema = _discoverability_value(command.get("arg_schema"))
        examples = _discoverability_examples(command.get("examples"))
        if not name or not description or not arg_schema or not examples:
            continue
        if include_target:
            execution_target = _discoverability_value(command.get("execution_target"))
            if not execution_target:
                continue
            rows.append((name, description, arg_schema, examples, execution_target))
            continue
        rows.append((name, description, arg_schema, examples))
    return tuple(rows)


def build_help_panel(
    *,
    commands: Sequence[Mapping[str, object]],
    profile: TerminalProfile,
) -> Panel:
    """Build deterministic command help panel with descriptions, args, and examples."""
    token = style_token_for(profile=profile, state=OutputState.RESULT)
    rows = _discoverability_rows(commands, include_target=False)
    table = Table(show_header=True, box=None, pad_edge=False)
    table.add_column("Command", style=token.title_style, no_wrap=True)
    table.add_column("Description", style=token.body_style)
    table.add_column("Arguments", style=token.body_style, no_wrap=True)
    table.add_column("Examples", style=token.body_style)
    for name, description, arg_schema, examples in rows:
        table.add_row(
            Text(name, style=token.title_style),
            Text(description, style=token.body_style),
            Text(arg_schema, style=token.body_style),
            Text(examples, style=token.body_style),
        )

    body = Group(Text("Available commands", style=token.body_style), table)
    return Panel(
        body,
        title=_panel_title(token, "Help"),
        border_style=token.border_style,
        expand=False,
    )


def build_introspection_panel(
    *,
    commands: Sequence[Mapping[str, object]],
    profile: TerminalProfile,
) -> Panel:
    """Build deterministic command introspection panel with execution targets."""
    token = style_token_for(profile=profile, state=OutputState.RESULT)
    rows = _discoverability_rows(commands, include_target=True)
    table = Table(show_header=True, box=None, pad_edge=False)
    table.add_column("Command", style=token.title_style, no_wrap=True)
    table.add_column("Description", style=token.body_style)
    table.add_column("Arguments", style=token.body_style, no_wrap=True)
    table.add_column("Examples", style=token.body_style)
    table.add_column("Execution Target", style=token.body_style, no_wrap=True)
    for name, description, arg_schema, examples, execution_target in rows:
        table.add_row(
            Text(name, style=token.title_style),
            Text(description, style=token.body_style),
            Text(arg_schema, style=token.body_style),
            Text(examples, style=token.body_style),
            Text(execution_target, style=token.body_style),
        )

    body = Group(Text("Command execution targets", style=token.body_style), table)
    return Panel(
        body,
        title=_panel_title(token, "Command Introspection"),
        border_style=token.border_style,
        expand=False,
    )


def _strip_sensitive_values(value: object) -> object:
    if isinstance(value, Mapping):
        sanitized: dict[str, object] = {}
        for key in sorted(value):
            normalized_key = str(key)
            if is_sensitive_key(normalized_key):
                continue
            sanitized[normalized_key] = _strip_sensitive_values(value[key])
        return sanitized
    if isinstance(value, Sequence) and not isinstance(value, str):
        return [_strip_sensitive_values(item) for item in value]
    return value


def _format_confirmation_field(key: str, value: object) -> str | None:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (int, float, str)):
        return str(value)
    if key in {"targets", "capabilities"} and isinstance(value, list):
        string_values = [item for item in value if isinstance(item, str)]
        if not string_values:
            return None
        return ", ".join(string_values)
    return None


def extract_confirmation_rows(summary: Mapping[str, object]) -> tuple[tuple[str, str], ...]:
    """Extract deterministic, safe summary rows for confirmation rendering."""
    sanitized = _strip_sensitive_values(summary)
    if not isinstance(sanitized, dict):
        return ()

    rows: list[tuple[str, str]] = []
    for key in _CONFIRMATION_FIELD_ORDER:
        if key not in sanitized:
            continue
        value = _format_confirmation_field(key, sanitized[key])
        if value is None:
            continue
        rows.append((_CONFIRMATION_FIELD_LABELS[key], value))

    planned_actions = sanitized.get("planned_sensitive_actions")
    if isinstance(planned_actions, list):
        rows.append(("Planned Actions", str(len(planned_actions))))

    return tuple(rows)


def build_confirmation_summary_panel(
    *,
    summary: Mapping[str, object],
    profile: TerminalProfile,
) -> Panel:
    """Build a high-impact pre-confirmation summary panel."""
    token = style_token_for(profile=profile, state=OutputState.CONFIRMATION)
    rows = extract_confirmation_rows(summary)

    table = Table(show_header=False, box=None, pad_edge=False)
    table.add_column(style=token.title_style, no_wrap=True)
    table.add_column(style=token.body_style)
    for key, value in rows:
        table.add_row(key, value)

    body = Group(
        Text("Review this high-impact summary before confirmation.", style=token.body_style),
        table,
    )
    return Panel(
        body,
        title=_panel_title(token, "Pre-Confirmation Summary"),
        border_style=token.border_style,
        expand=False,
    )
