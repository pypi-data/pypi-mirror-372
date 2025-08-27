"""Tests for the database."""

from unittest.mock import Mock, patch


def test_get_close_db(app):
    # Access the database
    with app.app_context():
        session = app.db.session
        assert session is app.db.session
    # Check that the session ended
    assert session is not app.db.session


def test_database(app):
    table_names = ("entries", "authorized_entries", "alt_authorized_entries")
    assert all(name in app.db.tables for name in table_names)


@patch(
    "dry_foundation.config.default_settings.Path.is_file", new=Mock(return_value=True)
)
def test_init_db_command_db_exists(runner):
    result = runner.invoke(args=["init-db"])
    assert "Database exists" in result.output


@patch(
    "dry_foundation.config.default_settings.Path.is_file", new=Mock(return_value=False)
)
@patch("dry_foundation.database.SQLAlchemy.initialize")
def test_init_db_command(mock_init_db, runner):
    result = runner.invoke(args=["init-db"])
    assert "Initialized" in result.output
    mock_init_db.assert_called_once()


@patch(
    "dry_foundation.config.default_settings.Path.is_file", new=Mock(return_value=False)
)
@patch("dry_foundation.database.SQLAlchemy.initialize")
def test_init_db_command_preload_path(mock_init_db, runner, client_context):
    with patch("flask.config.Config.get", side_effect=["/path/to/preload/data"]):
        result = runner.invoke(args=["init-db"])
        assert "Prepopulated" in result.output
        mock_init_db.assert_called_once()


@patch("sqlite3.connect")
def test_back_up_db_command(mock_connect_method, runner):
    db = mock_connect_method.return_value
    result = runner.invoke(args=["back-up-db"])
    backup_db = mock_connect_method.return_value
    assert "Backup complete" in result.output
    db.backup.assert_called_once_with(backup_db)
    # The `close` method should be called twice, once for each database
    assert mock_connect_method.return_value.close.call_count == 2
