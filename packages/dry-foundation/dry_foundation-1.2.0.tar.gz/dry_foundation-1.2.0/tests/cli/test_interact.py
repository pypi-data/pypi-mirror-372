"""Tests for the CLI."""

import os
from unittest.mock import patch

from dry_foundation.cli.interface import DryFlaskGroup, interact


class TestDryFlaskGroup:
    """Tests for the ``DryFlaskGroup`` object."""

    def test_initialization(self):
        DryFlaskGroup("test")
        assert os.environ.get("FLASK_APP") == "test"

    def test_help(self, runner):
        result = runner.invoke(args=["--help"])
        assert "Usage: test" in result.output


@patch("dry_foundation.cli.interface.DryFlaskGroup.main")
def test_interact(mock_cli_main):
    interact("test")
    mock_cli_main.assert_called_once()
