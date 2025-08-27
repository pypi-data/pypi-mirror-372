"""Utilities for general package functions."""

from datetime import datetime


def get_timestamp():
    """Get a timestamp for backup filenames."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")
