"""Smoke tests for the baseline ENDI scaffold."""

from typer.testing import CliRunner

from endi import __version__
from endi.cli import app


def test_package_version_is_set() -> None:
    assert __version__ == "0.1.0"


def test_cli_version_command_succeeds() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert f"ENDI {__version__}" in result.stdout
