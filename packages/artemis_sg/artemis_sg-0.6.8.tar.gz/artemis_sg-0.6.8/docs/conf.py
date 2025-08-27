from __future__ import annotations

import os
import sys

from artemis_sg._version import __version__ as asg_version

sys.path.insert(0, os.path.abspath(".."))

project = "artemis_sg"
copyright = "2023, Artemis Books"  # noqa: A001
author = "Artemis Books"
version = release = asg_version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosectionlabel",
    "sphinx_autodoc_typehints",
    "sphinx_inline_tabs",
    "sphinx_copybutton",
    "sphinxcontrib.mermaid",
    "sphinx_click.ext",
]

source_suffix = [".rst", ".md"]
exclude_patterns = [
    "_build",
    "**.ipynb_checkpoints",
    "Thumbs.db",
    ".DS_Store",
    ".env",
    ".venv",
]

html_theme = "furo"
html_theme_options = {
    "light_logo": "artemis_logo.png",
    "dark_logo": "artemis_logo.png",
}

html_static_path = ["resources"]
myst_enable_extensions = [
    "colon_fence",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "openpyxl": ("https://openpyxl.readthedocs.io/en/stable/", None),
}

nitpick_ignore = [
    ("py:class", "_io.StringIO"),
    ("py:class", "_io.BytesIO"),
]

always_document_param_types = True
