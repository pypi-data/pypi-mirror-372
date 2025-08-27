#!/usr/bin/env python
"""
Define objects for launching the application.
"""

import json
import os
import time
import webbrowser

from werkzeug.serving import is_running_from_reloader

from ..database import back_up_db, init_db
from .console import echo_text


class Launcher:
    """A tool to build and execute Flask commands."""

    def __init__(
        self,
        context,
        mode_type,
        host=None,
        port=None,
    ):
        self.mode_type = mode_type
        # Set attributes to govern launch control flow
        self.host = host if host else "127.0.0.1"
        self.port = port if port else mode_type.default_port
        self.app = self._initialize_application(context)

    def _initialize_application(self, context):
        application = self._build_application(context)
        if not self.is_loaded:
            init_db()
        return application

    def _build_application(self, context):
        self._app_mode = self.mode_type(context, host=self.host, port=self.port)
        self._app_name = self._app_mode.application.config["NAME"]
        # Set some application specific environment variables
        env_var_prefix = self._app_mode.application.config["SLUG"].upper()
        self._loaded_env_var = f"{env_var_prefix}_LOADED"
        self._browser_env_var = f"{env_var_prefix}_BROWSER"

    def launch(self, back_up=None, use_browser=False):
        """Launch the application."""
        if back_up:
            back_up_db()
        open_browser_criteria = [
            use_browser,
            not self.has_browser,
            not is_running_from_reloader(),
        ]
        if all(open_browser_criteria):
            self.open_browser()
        try:
            self._run_application()
        finally:
            self._close_application()

    def _run_application(self):
        if not self.is_loaded:
            echo_text(
                f"Running the {self._app_name} application...\n", color="deep_sky_blue1"
            )
            self.is_loaded = True
        self._app_mode.run()

    def _close_application(self):
        if not (is_running_from_reloader() or self._app_mode.name == "production"):
            echo_text(f"\nClosing the {self._app_name} app...")
            self.is_loaded = False

    def open_browser(self, delay=0):
        """Open the default web browser."""
        if self._app_mode.name in ("development", "local"):
            time.sleep(delay)
            webbrowser.open_new(f"http://{self.host}:{self.port}/")
            self.has_browser = True
        else:
            raise RuntimeError(
                "Opening the browser is only supported in development or local mode."
            )

    @property
    def is_loaded(self):
        return self._get_boolean_env_variable(self._loaded_env_var)

    @is_loaded.setter
    def is_loaded(self, value):
        self._set_booean_env_variable(self._loaded_env_var, value)

    @property
    def has_browser(self):
        return self._get_boolean_env_variable(self._browser_env_var)

    @has_browser.setter
    def has_browser(self, value):
        self._set_booean_env_variable(self._browser_env_var, value)

    @staticmethod
    def _get_boolean_env_variable(name):
        value = os.environ.get(name)
        # Flask parses environment variables using JSON
        return bool(json.loads(value) if value else value)

    @staticmethod
    def _set_booean_env_variable(name, value):
        if value:
            os.environ[name] = "true"
        else:
            os.environ.pop(name)
