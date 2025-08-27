"""
Expose commonly used database functionality to the rest of the package.
"""

import sqlite3
from pathlib import Path

from flask import current_app
from flask.cli import with_appcontext

from ..cli.console import echo_text
from ..utils import get_timestamp
from .interface import SQLAlchemy, db_transaction

__all__ = [
    "db_transaction",
    "SQLAlchemy",
]


@with_appcontext
def init_db():
    """Initialize the database (if it does not already exist)."""
    echo_db_info("Initializing the database...")
    db_path = current_app.config["DATABASE"]
    if not db_path.is_file():
        current_app.db.initialize(current_app)
        echo_db_info(f"Initialized the database ('{db_path}')")
        if preload_path := current_app.config.get("PRELOAD_DATA_PATH"):
            echo_db_info(f"Prepopulated the database using '{preload_path}'")
    else:
        echo_db_info(f"Database exists, using '{db_path}'")


@with_appcontext
def back_up_db():
    """Create a backup of the database."""
    echo_db_info("Backing up the database...")
    timestamp = get_timestamp()
    # Connect to the databases and back it up
    db = sqlite3.connect(current_app.config["DATABASE"])
    with (backup_db := _connect_to_backup_database(current_app, timestamp)):
        db.backup(backup_db)
    # Close the connections
    backup_db.close()
    db.close()
    echo_db_info(f"Backup complete ({timestamp})")


def _connect_to_backup_database(current_app, timestamp):
    backup_db_dir_path = Path(current_app.instance_path) / "db_backups"
    # Create the directory if it does not already exist
    backup_db_dir_path.mkdir(exist_ok=True, parents=True)
    # Connect to (and create) the backup directory with proper timestamp
    backup_db_path = backup_db_dir_path / f"backup_{timestamp}.sqlite"
    backup_db = sqlite3.connect(backup_db_path)
    return backup_db


def echo_db_info(text):
    """Echo text to the terminal for database-related information."""
    echo_text(text, color="deep_sky_blue1")
