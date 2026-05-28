"""Target policy loading for ENDI red-team lab profiles."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DEFAULT_MAX_POLICY_BYTES = 64 * 1024


class TargetPolicyError(ValueError):
    """Structured target policy validation failure."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class TargetPolicy:
    """Loaded target policy content."""

    path: Path
    content: str


def load_target_policy(
    path: str,
    *,
    max_bytes: int = DEFAULT_MAX_POLICY_BYTES,
) -> TargetPolicy:
    """Load and validate a UTF-8 target policy file."""
    policy_path = Path(path).expanduser()
    if not policy_path.exists() or not policy_path.is_file():
        raise TargetPolicyError(
            "target_policy_missing",
            "Target policy file does not exist.",
        )

    try:
        size = policy_path.stat().st_size
    except OSError as exc:
        raise TargetPolicyError(
            "target_policy_unreadable",
            "Target policy file cannot be inspected.",
        ) from exc

    if size > max_bytes:
        raise TargetPolicyError(
            "target_policy_too_large",
            f"Target policy file exceeds {max_bytes} bytes.",
        )

    try:
        content = policy_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise TargetPolicyError(
            "target_policy_not_utf8",
            "Target policy file must be valid UTF-8.",
        ) from exc
    except OSError as exc:
        raise TargetPolicyError(
            "target_policy_unreadable",
            "Target policy file cannot be read.",
        ) from exc

    if not content.strip():
        raise TargetPolicyError(
            "target_policy_empty",
            "Target policy file must not be empty.",
        )

    return TargetPolicy(path=policy_path, content=content)
