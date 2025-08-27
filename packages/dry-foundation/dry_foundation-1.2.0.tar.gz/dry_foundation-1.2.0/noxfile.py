"""The top-level Nox specification."""

import shutil
from pathlib import Path

import nox

PACKAGE = "dry_foundation"
PACKAGE_DIR = Path("src", PACKAGE)
PYTHON_PROJECT_FILES = [
    "src/",
    "tests/",
    "noxfile.py",
]

#
# --- TESTING ---
#

PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]


@nox.session(name="clean-coverage")
def clean_coverage(session):
    session.install("coverage")
    session.run("coverage", "erase")


@nox.session(name="test", python=PYTHON_VERSIONS, requires=["clean-coverage"])
def test_package(session):
    session.install("-e", ".[test]")
    try:
        session.run("coverage", "run", "-m", "pytest")
    finally:
        session.run("coverage", "report", "--show-missing", "--include", "tests/*")
        session.run("coverage", "report", "--show-missing", "--include", "src/*")
        session.run("coverage", "html")


#
# --- DOCS ---
#

DOCS_DIR = Path("docs")
DOCS_SRC = DOCS_DIR / "source"
DOCS_SRC_API = DOCS_SRC / "api"
DOCS_BUILD = DOCS_DIR / "build"
DOCS_HTML = DOCS_BUILD / "html"


@nox.session(name="docs")
def build_docs(session):
    session.install("-e", ".[docs]")
    shutil.rmtree(DOCS_SRC_API)
    session.run("sphinx-apidoc", "-f", "-o", DOCS_SRC_API, PACKAGE_DIR)
    session.run("sphinx-build", "-b", "html", DOCS_SRC, DOCS_HTML)


#
# --- LINTING ---
#

LINTING_DEPS = ["ruff==0.12.8"]


@nox.session
def lint(session):
    session.install(*LINTING_DEPS)
    session.run("ruff", "check", *PYTHON_PROJECT_FILES)


#
# --- FORMATTING ---
#

FORMAT_DEPS = ["ruff==0.12.8"]
PYTHON_FORMAT_FILES = [
    *PYTHON_PROJECT_FILES,
    DOCS_SRC / "conf.py",
]


@nox.session(name="format")
def format_code(session):
    session.install(*FORMAT_DEPS)
    # ruff does not sort imports by default
    # (https://docs.astral.sh/ruff/formatter/#sorting-imports)
    session.run("ruff", "check", "--select", "I", "--fix")
    session.run("ruff", "format", *PYTHON_FORMAT_FILES)


@nox.session(name="format-diff")
def diff_format(session):
    session.install(*FORMAT_DEPS)
    session.run("ruff", "format", "--diff", *PYTHON_FORMAT_FILES)
    session.run("ruff", "format", "--diff", *PYTHON_FORMAT_FILES)


@nox.session(name="format-check")
def check_format(session):
    session.install(*FORMAT_DEPS)
    session.run("ruff", "format", "--check", *PYTHON_FORMAT_FILES)
    session.run("ruff", "format", "--check", *PYTHON_FORMAT_FILES)


#
# --- PACKAGING ---
#

PACKAGING_DEPS = [
    "hatch",
]


@nox.session(name="package")
def build_package(session):
    session.install(*PACKAGING_DEPS)
    session.run("hatch", "build")


@nox.session(name="publish")
def publish_package(session):
    session.install(*PACKAGING_DEPS)
    with open(".TOKEN") as token_file:
        token = token_file.read()
    session.run("hatch", "publish", "--user", "__token__", "--auth", token)
