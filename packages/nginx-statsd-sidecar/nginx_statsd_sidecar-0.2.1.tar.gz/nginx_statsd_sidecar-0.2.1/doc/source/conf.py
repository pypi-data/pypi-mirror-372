# Configuration file for the Sphinx documentation builder.  # noqa: INP001
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
from __future__ import annotations

import os
import sys
from typing import Any

import sphinx_rtd_theme  # noqa: F401

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

sys.path.insert(0, os.path.abspath("../.."))  # noqa: PTH100

# -- Project information -----------------------------------------------------

# the master toctree document
master_doc = "index"

project = "nginx_statsd_sidecar"
copyright = "Caltech IMSS ADS"  # noqa: A001
author = "Caltech IMSS ADS"

# The full version, including alpha/beta/rc tags
release = "0.2.1"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinxcontrib.images",
    "sphinx.ext.intersphinx",
    "sphinx_rtd_theme",
]

source_suffix: str = ".rst"

# Add any paths that contain templates here, relative to this directory.
templates_path: list[str] = ["_templates"]

autodoc_member_order: str = "groupwise"

# Make Sphinx not expand all our Type Aliases
autodoc_type_aliases: dict[str, str] = {}

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns: list[str] = ["_build"]

# the locations and names of other projects that should be linked to this one
intersphinx_mapping: dict[str, tuple[str, str | None]] = {
    "python": ("https://docs.python.org/3", None),
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme: str = "sphinx_rtd_theme"

html_show_sourcelink: bool = False
html_show_sphinx: bool = False
html_show_copyright: bool = True
html_theme_options: dict[str, Any] = {"collapse_navigation": False}
