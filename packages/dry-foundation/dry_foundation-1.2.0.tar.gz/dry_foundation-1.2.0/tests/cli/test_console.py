"""Tests for CLI console functionality."""

from dry_foundation.cli.console import echo_text


def test_echo_text(capsys):
    echo_text("test")
    assert "test" in capsys.readouterr().out
