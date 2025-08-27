"""Tests for the application factory."""

from unittest.mock import Mock, patch

import pytest

from dry_foundation.config.settings import TestingConfig as _TestingConfig
from dry_foundation.factory import DryFlask, Factory


@patch("dry_foundation.factory.Factory.default_db_interface")
def test_factory_decorator_no_args(mock_db_interface):
    mock_factory = Mock()
    decorator = Factory
    # Apply the decorator and check results
    decorated_factory = decorator(mock_factory)
    decorated_factory()
    mock_factory.assert_called_once()
    mock_db_interface.select_interface.assert_called_once()


def test_factory_decorator_with_args():
    mock_factory = Mock()
    mock_db_interface = Mock()
    decorator = Factory(db_interface=mock_db_interface)
    # Apply the decorator and check results
    decorated_factory = decorator(mock_factory)
    decorated_factory()
    mock_factory.assert_called_once()
    mock_db_interface.select_interface.assert_called_once()


def test_invalid_application_config():
    with pytest.raises(TypeError):
        # This will fail because the `TestingConfig` is not instance-based
        DryFlask.set_default_config_type(_TestingConfig)
