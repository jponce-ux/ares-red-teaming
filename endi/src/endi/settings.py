"""Local ENDI runtime settings."""

from __future__ import annotations

import json
import os
from pathlib import Path

_CONFIG_ENV_VAR = "ENDI_CONFIG_PATH"
_XDG_CONFIG_ENV_VAR = "XDG_CONFIG_HOME"


def _default_config_path() -> Path:
    explicit_path = os.environ.get(_CONFIG_ENV_VAR)
    if explicit_path:
        return Path(explicit_path).expanduser()

    xdg_config_home = os.environ.get(_XDG_CONFIG_ENV_VAR)
    if xdg_config_home:
        return Path(xdg_config_home).expanduser() / "endi" / "config.json"

    return Path.home() / ".config" / "endi" / "config.json"


def load_chat_defaults() -> dict[str, object]:
    """Load remembered chat provider defaults."""
    config_path = _default_config_path()
    try:
        decoded = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(decoded, dict):
        return {}
    chat_defaults = decoded.get("chat")
    return dict(chat_defaults) if isinstance(chat_defaults, dict) else {}


def save_chat_defaults(defaults: dict[str, object]) -> None:
    """Persist chat provider defaults for future CLI invocations."""
    config_path = _default_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps({"chat": defaults}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
