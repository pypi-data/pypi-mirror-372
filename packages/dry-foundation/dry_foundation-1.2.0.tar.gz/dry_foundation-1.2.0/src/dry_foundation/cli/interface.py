#!/usr/bin/env python
"""
Elements for constructing scripts (entry points) that will launch the application.
"""

import os

import click
from flask.cli import FlaskGroup

from ..database import back_up_db, init_db
from .launcher import Launcher
from .modes import cli_modes


@click.command(
    "launch",
    help="Launch the application.",
)
@click.argument(
    "mode",
    type=click.Choice(cli_modes.keys(), case_sensitive=False),
)
@click.option("--host", "-h", type=click.STRING, help="The interface to bind to.")
@click.option("--port", "-p", type=click.INT, help="The port to bind to.")
@click.option(
    "--backup",
    is_flag=True,
    help="A flag indicating if the database should be backed up.",
)
@click.option(
    "--browser",
    is_flag=True,
    help=(
        "A flag indicating if a new browser window should be opened "
        "(development and local modes only)."
    ),
)
@click.pass_context
def launch_command(context, mode, host, port, backup, browser):
    """Run the app as a command line program."""
    app_launcher = Launcher(context, cli_modes[mode], host=host, port=port)
    app_launcher.launch(back_up=backup, use_browser=browser)


@click.command("init-db")
def init_db_command():
    """Initialize the database from the command line (if it does not already exist)."""
    init_db()


@click.command("back-up-db")
def back_up_db_command():
    """Back up the database from the command line."""
    back_up_db()


class DryFlaskGroup(FlaskGroup):
    """A special subclass of ``FlaskGroup`` with additional commands."""

    def __init__(self, name, app_name=None, **kwargs):
        # Set the `FLASK_APP` environment variable required by Flask
        os.environ["FLASK_APP"] = name
        app_name = app_name or name
        kwargs.setdefault("help", self._build_default_help_message(app_name))
        super().__init__(name=name, **kwargs)
        self.add_command(launch_command)
        self.add_command(init_db_command)
        self.add_command(back_up_db_command)

    def _build_default_help_message(self, app_name):
        return (
            f"CLI functionality for the {app_name} application.\n"
            "\n"
            "Built on Flask, this command line interface extends a typical Flask CLI "
            "to include additional commands for launching the application, "
            "initializing the application database, and backing up the application "
            "database."
        )

    def list_commands(self, ctx):
        # Prevent the list of commands from being sorted alphabetically
        # (and ensure that the launch command is the first entry)
        command_names = list(self.commands)
        command_names.remove(launch_command.name)
        command_names.insert(0, launch_command.name)
        return command_names


def interact(program_name):
    """A function to serve as a convenient entrypoint to a DRY application."""
    cli = DryFlaskGroup(name=program_name)
    cli.main()
