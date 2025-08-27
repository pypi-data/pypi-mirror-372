"""Tests for the application factory."""

import os
from unittest.mock import patch

import pytest

from dry_foundation.cli.launcher import Launcher
from dry_foundation.cli.modes import DevelopmentAppMode, ProductionAppMode


@pytest.fixture
def mock_browser():
    with patch("dry_foundation.cli.launcher.webbrowser") as mock_browser:
        yield mock_browser
    os.environ["TEST_BROWSER"] = "false"


class TestLauncher:
    """Tests for the ``Launcher`` object."""

    @patch("dry_foundation.cli.launcher.init_db")
    def test_launch(self, mock_init_method, mock_click_context):
        Launcher(mock_click_context, DevelopmentAppMode).launch()
        mock_init_method.assert_called_once()

    @patch("dry_foundation.cli.launcher.back_up_db")
    @patch("dry_foundation.cli.launcher.init_db")
    def test_launch_with_backup(
        self, mock_init_method, mock_back_up_method, mock_click_context
    ):
        Launcher(mock_click_context, DevelopmentAppMode).launch(back_up=True)
        mock_init_method.assert_called_once()
        mock_back_up_method.assert_called_once()

    @patch("dry_foundation.cli.launcher.init_db")
    def test_launch_with_browser(
        self, mock_init_method, mock_browser, mock_click_context
    ):
        Launcher(mock_click_context, DevelopmentAppMode).launch(use_browser=True)
        mock_init_method.assert_called_once()
        mock_browser.open_new.assert_called_once()

    @patch("dry_foundation.cli.launcher.init_db")
    @patch("gunicorn.app.base.BaseApplication.run")
    def test_launcher_invalid_browser_mode(
        self,
        mock_gunicorn_run_method,
        mock_init_method,
        mock_browser,
        mock_click_context,
    ):
        with pytest.raises(RuntimeError):
            Launcher(mock_click_context, ProductionAppMode).launch(use_browser=True)
