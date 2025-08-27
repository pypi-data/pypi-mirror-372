# DRY Foundation

<img src="img/logo/dry-logo.png" alt="DRY Foundation logo" />

Tools and components for building customized and consistent small-scale Flask applications.


## Why DRY?

**Don't Repeat Yourself.** Why write and maintain multiple copies of application infrastructure if it's going to be used and reused?

This package is designed to be a lightweight foundation a Flask application: it performs some of the database setup operations, coordinates database management for robust test suites, and also provides some utilities for enforcing authorization criteria for database access, among other things.

Here are some of the features explained in greater detail.


### Application Factories and Command Line Interfaces

The Flask command line interface (CLI) provides a lot of functionality via it's Click backend.
However, what if a user wishes to launch an application from the command line depending on a certain configuration.
The Flask documentation [shows an example of how to structure an application to leverage multiple configurations via objects](https://flask.palletsprojects.com/en/stable/config/#development-production), but leaves it up to a user to implement the mechanics of passing this configuration to the application via environment variable or some other script.

This package takes a different approach, and provides tools to customize the CLI so that configurations can be loaded dynamically at runtime.
Configurations are predefined (for production, development, and testing), and can be loaded by specifying a launch mode:

- **Production Mode:** Launch an app for production use, drawing from a production-style configuration.
- **Local Mode:** Launch an app for local use, using the Flask development server but still relying on a production-style configuration.
- **Development Mode:** Launch an app for development, with default debugging features and using a development style configuration.

A testing configuration is also built-in to provide test-specific configuration settings.


### Database Setup

One element of an application foundation is the testing infrastructure.
[Flask gives some guidance in the current edition of their documentation](https://flask.palletsprojects.com/en/2.3.x/tutorial/tests/#setup-and-fixtures), and it suggests creating a temporary SQLite database for each test.
This is perfectly fine for simple applications, but adds substantial overhead (and test time) to applications with many tests, especially for those where the database contains some preloaded information.
Instead, it would be preferable to create and use one temporary database instance for the majority of tests that only require read-access to the database, and then only create additional test databases for the tests that modify the state of the database (e.g., SQLAlchemy transactions).[^mocking]

_DRY Foundation_ provides the infrastructure to create databases in both of these cases: a "persistent" database for read-only tests, and "ephemeral" databases for each transaction).
The persistent test database is used by default, but a `transaction_lifetime` decorator can be used to indicate that a given test should use an ephemeral copy.

[^mocking]: Yes, you could also just not create databases and mock the database return functions, but my experience has been that it is even more tedious to maintain a comprehensive set of mocked data to test various intricacies and edge cases while simultaneously ensuring that the mocks behave similarly enough to SQLAlchemy objects.


### Authorization and Data Handlers

The common operations are easy to do using SQLAlchemy, but rather than rolling new functions for each new query in every application, this tool provides a set of handlers that are designed to abstract away a bunch of the tedious details.
Also, my experience is that enforcing authorization constraints when manipulating sophisticated table relationships can be tricky, and so this tool and its handlers provide an interface for managing those authorizations consistently.

It's possible I'm missing a key functionality of SQLAlchemy that enables this behavior elegantly, but I haven't found a satisfiably clean way to do it yet.
Until I become so enlightened, this package creates an interface where each model may define the chain of joins required to establish whether it belongs to an authorized user, and then a handler to query the database and perform those joins for each query.
This is designed to be extensible, since I often want this behavior available for the majority of ORM models in my application.

If you happen to read this and think "This dude's dumb; why on Earth didn't he use _this_ functionality baked into SQLAlchemy?" drop me a line because I'm interested to know what I'm missing.


## Installation

_DRY Foundation_ is registered on the [Python Package Index (PyPI)](https://pypi.org/project/...) for easy installation.
To install the package, simply run

```
pip install dry-foundation
```

The package requires a recent version of Python (3.10+).


## Usage

The app has lots of tools, but the basics can be used just as drop-in replacements for the standard `Flask` object and application factory.

```python
# DRY Application:  `dry_application/__init__.py`

from dry_foundation import DryFlask, Factory

@Factory
def create_app(config=None):
    app = DryFlask(__name__, app_name="DRY Application")
    app.configure(config)
    # Anything else performed by the application factory...
    return app
```

For a more complete, up-to-date API reference, build and read the docs:

```bash
make docs
# open `docs/build/html/index.html` in your browser
```


## License

This project is licensed under the GNU General Public License, Version 3.
It is fully open-source, and while you are more than welcome to fork, add, modify, etc. it is required that you keep any distributed changes and additions open-source.


## Changes

Changes between versions are tracked in the [changelog](./CHANGELOG.md).
