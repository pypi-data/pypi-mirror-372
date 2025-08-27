PYTHON = python3.11
# Package
PACKAGE = dry_foundation
PACKAGE_DIR = src/$(PACKAGE)
PACKAGE_PYTHON_FILES = $(wildcard $(PACKAGE_DIR)/*.py) \
		       $(wildcard $(PACKAGE_DIR)/**/*.py)
# Requirements files
REQS = requirements.txt
# Package environment (for building and testing)
ENV = dry-env
ENV_BIN = $(ENV)/bin

NOX = $(ENV_BIN)/nox

# Documentation locations
DOCS = docs
DOCS_SRC = $(DOCS)/source
DOCS_SRC_API = $(DOCS_SRC)/api
DOCS_BUILD = $(DOCS)/build
DOCS_HTML = $(DOCS_BUILD)/html

# Format files
PYTHON_FORMAT_FILES = $(PACKAGE_PYTHON_FILES) $(TEST_PYTHON_FILES)
