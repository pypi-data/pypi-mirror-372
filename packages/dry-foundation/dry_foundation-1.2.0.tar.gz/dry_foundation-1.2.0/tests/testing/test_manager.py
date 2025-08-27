"""Tests for the test manager."""

import pytest

from dry_foundation.testing import transaction_lifetime


class TestAppTestManager:
    """Tests for the ``AppTestManager`` object."""

    ephemeral_apps = []

    def test_nontransaction(self, app_test_manager, app):
        assert app is app_test_manager.persistent_app
        assert app is not app_test_manager.ephemeral_app

    @pytest.mark.parametrize("execution_count", range(3))
    @transaction_lifetime
    def test_transaction(self, app_test_manager, app, execution_count):
        assert app is not app_test_manager.persistent_app
        assert app is app_test_manager.ephemeral_app
        assert app not in self.ephemeral_apps
        self.ephemeral_apps.append(app)
