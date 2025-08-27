# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import sys
from pathlib import Path

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "DRY Foundation"
copyright = "2025, Mitch Negus"
author = "Mitch Negus"

# Get the release (e.g, version info excluding commit, dirty directory, etc.)
from importlib import metadata

version = metadata.version("dry-foundation")
release = version.split("+")[0]

package_path = Path(__file__).parents[2] / "src/dry_foundation"
sys.path.insert(0, str(package_path.absolute()))


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "myst_parser",
]

templates_path = ["_templates"]
root_doc = "contents"
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]


# -- MyST configuration

myst_enable_extensions = ["html_image"]
