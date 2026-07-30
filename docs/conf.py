# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import sys
from pathlib import Path

sys.path.insert(0, str(Path().resolve()))

import undate

# -- Project information -----------------------------------------------------

project = "undate"
copyright = "2026, DHtech"
author = "DHtech Community"

# The full version, including alpha/beta/rc tags
release = undate.__version__  # type: ignore[attr-defined]

master_doc = "index"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "myst_parser",
    "sphinx_pyodide",
]

# build static output for noscript fallback
pyodide_build_output = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = ["custom.css"]

html_theme_options = {
    "light_logo": "undate_logo.svg",
    "dark_logo": "undate_logo_dark.svg",
    "source_repository": "https://github.com/dh-tech/undate-python",
    "source_branch": "main",
    "source_directory": "docs/",
    "light_css_variables": {
        "color-brand-primary": "#6670bb",
        "color-brand-content": "#6670bb",
        "color-background-primary": "#f0f1f8",
        "color-background-secondary": "#e5e7f2",
        "sidebar-logo-width": "200px",
    },
    "dark_css_variables": {
        "color-brand-primary": "#9198d0",
        "color-brand-content": "#9198d0",
        "color-background-primary": "#1d202f",
        "color-background-secondary": "#151825",
        "sidebar-logo-width": "200px",
    },
}

# turn on relative links; make sure both github and sphinx links work
# myst_enable_extensions = ["linkify"]  # disabling because not found
