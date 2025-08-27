"""
An interface for connecting to and working with the SQLite database.
"""

import functools

from flask import current_app
from sqlalchemy import URL, create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .schema import ViewAwareMetaData

DIALECT = "sqlite"
DBAPI = "pysqlite"


class SQLAlchemy:
    """
    Store an interface to SQLAlchemy database objects.

    This creates, stores, and manages an interface to work with
    SQLAlchemy objects. At the class level, it stores a reference to
    the current database metadata and a reference to the currently
    active interface instance. That instance can be used to set up
    the database engine and tables with consistent parameters, open
    and close sessions, as well as select an interface instance to use.
    Most often, this interface instance will be the default interface
    defined by an application; however, when testing, this may be a
    new interface used for only a subset of tests.

    Parameters
    ----------
    echo_engine : bool, optional
        A flag passed to the interface's engine indicating if output
        should be echoed. The default is `False`.
    """

    metadata = ViewAwareMetaData()
    default_interface = None

    def __init__(self, echo_engine=False):
        self.engine = None
        self.scoped_session = None
        self.echo_engine = echo_engine

    @property
    def tables(self):
        return self.metadata.tables

    @property
    def session(self):
        # Returns the current `Session` object
        return self.scoped_session()

    def setup_engine(self, db_path, echo_engine=None):
        """
        Setup the database engine, a session factory, and metadata.

        Parameters
        ----------
        db_path : os.PathLike
            The path to the local database.
        """
        echo_engine = self.echo_engine if echo_engine is None else echo_engine
        # Create the engine using the customodatabase URL
        db_url = URL.create(drivername=f"{DIALECT}+{DBAPI}", database=str(db_path))
        self.engine = create_engine(db_url, echo=echo_engine)
        # Use a session factory to generate sessions
        session_factory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            future=True,
        )
        self.scoped_session = scoped_session(session_factory)

    def initialize(self, app):
        """
        Initialize the database.

        Initialize the database, possibly using any additional arguments
        necessary. This method is designed to be extended by
        app-specific interfaces with customized initialization
        procedures.

        Parameters
        ----------
        app : flask.Flask
            The app object, which may pass initialization parameters via
            its configuration.
        """
        self.create_tables()

    def create_tables(self):
        """Create tables from the model metadata."""
        self.metadata.create_all(bind=self.engine)

    def close(self, exception=None):
        """Close the database if it is open."""
        if self.scoped_session is not None:
            self.scoped_session.remove()

    @classmethod
    def create_default_interface(cls, *args, **kwargs):
        """Create a default interface for the app."""
        cls.default_interface = cls(*args, **kwargs)

    @classmethod
    def select_interface(cls, app, echo_engine=False):
        """
        Choose the database interface.

        Assign a database interface to the given application. This will
        either create a new interface (e.g., during testing) and assign
        it to the application object or assign an existing (default)
        interface previously instantiated by the application. This
        selector assumes that the path to the local database instance
        will be provided by the app's configuration.

        Parameters
        ----------
        app_factory_func : callable
            The Flask app factory function.
        echo_engine : bool, optional
            A flag passed to the interface's engine indicating if output
            should be echoed. The default is `False`.

        Returns
        -------
        decorator : func
            The wrapped factory function that sets the databse interface.
        """
        # Prepare database access with SQLAlchemy:
        # - Use the `app.db` attribute like the `app.extensions` dict
        #   (but not actually that dict because this is not an extension)
        if not app.testing:
            if not cls.default_interface:
                cls.create_default_interface()
            app.db = cls.default_interface
        else:
            app.db = cls(
                *app.config.get("DATABASE_INTERFACE_ARGS", []),
                **app.config.get("DATABASE_INTERFACE_KWARGS", {}),
            )
        app.db.setup_engine(db_path=app.config["DATABASE"], echo_engine=echo_engine)
        # Establish behavior for closing the database
        app.teardown_appcontext(app.db.close)
        # If testing, the database still needs to be initialized/prepopulated
        # (otherwise, database initialization is typically executed via the CLI)
        if app.testing:
            app.db.initialize(app)


def db_transaction(func):
    """A decorator denoting the wrapped function as a database transaction."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with current_app.db.session.begin():
            return func(*args, **kwargs)

    return wrapper


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
