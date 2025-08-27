"""Tests for application configuration objects."""

from pathlib import Path
from unittest.mock import patch

from dry_foundation.config import (
    DevelopmentConfig,
    ProductionConfig,
)
from dry_foundation.config import (
    TestingConfig as _TestingConfig,  # rename to avoid pytest collection
)

APP_IMPORT_NAME = "test"


def test_production_config(instance_path):
    config = ProductionConfig(APP_IMPORT_NAME, instance_path)
    assert config.SECRET_KEY == "INSECURE"


def test_production_config_default_file(instance_path, default_config_filepath):
    with patch.object(
        ProductionConfig, "default_config_filepaths", new=[default_config_filepath]
    ):
        config = ProductionConfig(APP_IMPORT_NAME, instance_path)
        assert config.SECRET_KEY == "test secret key"


def test_production_config_instance_file_supersedes(
    instance_path, default_config_filepath, instance_config_filepath
):
    with patch.object(
        ProductionConfig, "default_global_config_filepath", new=default_config_filepath
    ):
        config = ProductionConfig(APP_IMPORT_NAME, instance_path)
        assert config.SECRET_KEY == "test secret key"
        assert config.OTHER == "test supersede"


def test_development_config(instance_path):
    config = DevelopmentConfig(APP_IMPORT_NAME, instance_path)
    assert config.SECRET_KEY == "development key"


def test_testing_config():
    mock_db_path = Path("/path/to/test/db.sqlite")
    config = _TestingConfig(APP_IMPORT_NAME, db_path=mock_db_path)
    assert config.SECRET_KEY == "testing key"
    assert config.DATABASE == mock_db_path
