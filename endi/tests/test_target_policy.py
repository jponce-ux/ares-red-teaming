"""Tests for ENDI target policy loading."""

from pathlib import Path

import pytest

from endi.target_policy import TargetPolicyError, load_target_policy


def test_load_target_policy_reads_utf8_text(tmp_path: Path) -> None:
    policy_path = tmp_path / "policy.md"
    policy_path.write_text("ENDI policy\n\nRule R1", encoding="utf-8")

    policy = load_target_policy(str(policy_path))

    assert policy.content == "ENDI policy\n\nRule R1"
    assert policy.path == policy_path


def test_load_target_policy_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(TargetPolicyError) as exc_info:
        load_target_policy(str(tmp_path / "missing.md"))

    assert exc_info.value.code == "target_policy_missing"


def test_load_target_policy_rejects_empty_file(tmp_path: Path) -> None:
    policy_path = tmp_path / "empty.md"
    policy_path.write_text("   \n", encoding="utf-8")

    with pytest.raises(TargetPolicyError) as exc_info:
        load_target_policy(str(policy_path))

    assert exc_info.value.code == "target_policy_empty"


def test_load_target_policy_rejects_non_utf8_file(tmp_path: Path) -> None:
    policy_path = tmp_path / "binary.md"
    policy_path.write_bytes(b"\xff\xfe\x00")

    with pytest.raises(TargetPolicyError) as exc_info:
        load_target_policy(str(policy_path))

    assert exc_info.value.code == "target_policy_not_utf8"


def test_load_target_policy_rejects_oversized_file(tmp_path: Path) -> None:
    policy_path = tmp_path / "large.md"
    policy_path.write_text("x" * 1025, encoding="utf-8")

    with pytest.raises(TargetPolicyError) as exc_info:
        load_target_policy(str(policy_path), max_bytes=1024)

    assert exc_info.value.code == "target_policy_too_large"
