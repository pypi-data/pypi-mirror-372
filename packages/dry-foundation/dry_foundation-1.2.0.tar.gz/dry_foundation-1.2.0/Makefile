# Include variables
include config.mk


## install	: Install the package
.PHONY: install
install :
	pip install .


## develop 	: Install the package in development mode
.PHONY: develop
develop :
	pip install -e .


## env		: Prepare a virtual environment to run the package
.PHONY: env
env : $(ENV)/.touchfile
	@echo "The environment ($(ENV)) is up to date."


# Create/update the virtual environment (based on `requirements.txt`, etc.)
# Uses touchfile as proxy for installed environment
$(ENV)/.touchfile : $(REQS) pyproject.toml
	@echo "Installing/updating the environment ($(ENV))."
	@if [ ! -d "$(ENV)" ]; then $(PYTHON) -m venv $(ENV); fi
	@$(ENV_BIN)/pip install -r $(REQS) -e .
	@touch $(ENV)/.touchfile


## docs 		: Build documentation
.PHONY: docs
docs : env
	@$(NOX) -s docs


## test		: Run tests
.PHONY: test
test : env
	@$(NOX) -s test


## lint		: Lint the package source code
.PHONY: lint
lint: env
	@$(NOX) -s lint


## format		: Format the package source code
.PHONY: format
format : env
	@$(NOX) -s format


## format-diff	: See the differences that will be produced by formatting
.PHONY: format-diff
format-diff : env
	@$(NOX) -s format-diff


## package	: Bundle the package for distribution
.PHONY: package
package : env
	@$(NOX) -s package


## upload		: Upload the package to PyPI
.PHONY: upload
upload : env
	@$(NOX) -s publish


## clean		: Clean all automatically generated files
.PHONY : clean
clean :
	@rm -rf $(PACKAGE_DIR)/_version.py
	@rm -rf htmlcov/
	@rm -rf dist/ *egg-info/
	@rm -rf .pytest_cache/
	@rm -rf $(DOCS_SRC_API)
	@rm -rf $(ENV)


.PHONY: help
help : Makefile
	@sed -n 's/^##//p' $<
