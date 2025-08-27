import json
from unittest.mock import Mock

import pytest

from dry_foundation.testing import AppTestManager

from testing_helpers import (
    AlternateAuthorizedEntry,
    AuthorizedEntry,
    Entry,
    create_test_app,
)


class DryFoundationAppTestManager(AppTestManager):
    """
    A test manager for the Dry Foundation package.

    Although Dry Foundation is not itself a Flask app, this test manager
    exists to test that the package works properly when applied to other
    test apps.
    """

    def prepare_test_database(self, db):
        with db.session.begin():
            entries = [
                Entry(x=1, y="ten", user_id=1),
                Entry(x=2, y="eleven", user_id=1),
                Entry(x=3, y="twelve", user_id=1),
                Entry(x=4, y="twenty", user_id=2),
                AuthorizedEntry(a=1, b="one", c=1),
                AuthorizedEntry(a=2, b="two", c=1),
                AuthorizedEntry(a=3, b="three", c=4),
                AlternateAuthorizedEntry(p=1, q=1),
                AlternateAuthorizedEntry(p=2, q=2),
                AlternateAuthorizedEntry(p=3, q=2),
                AlternateAuthorizedEntry(p=4, q=3),
            ]
            db.session.add_all(entries)


# Instantiate the app manager to determine the correct app (persistent/ephemeral)
app_manager = DryFoundationAppTestManager(import_name="test", factory=create_test_app)


@pytest.fixture(scope="session")
def app_test_manager():
    # Provide access to the app test manager as a fixture
    return app_manager


@pytest.fixture
def app():
    return app_manager.get_app()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def client_context(client):
    with client:
        # Context variables (e.g., `g`) may be accessed only after response
        client.get("/")
        yield


@pytest.fixture
def mock_click_context():
    context = Mock()
    context.obj.create_app = create_test_app
    # Dynamically call the (current) `create_app` via the mocked `load_app`
    context.obj.load_app = lambda: getattr(context.obj, "create_app")()
    return context


@pytest.fixture
def instance_path(tmp_path):
    instance_dir = tmp_path / "instance"
    instance_dir.mkdir()
    return instance_dir


@pytest.fixture
def instance_config_filepath(instance_path):
    config_filepath = instance_path / "test-config.json"
    with config_filepath.open("w") as test_config_file:
        json.dump({"OTHER": "test supersede"}, test_config_file)
    return config_filepath


@pytest.fixture
def default_config_filepath(tmp_path):
    config_filepath = tmp_path / "test-config.json"
    with config_filepath.open("w") as test_config_file:
        json.dump({"SECRET_KEY": "test secret key", "OTHER": "other"}, test_config_file)
    return config_filepath
