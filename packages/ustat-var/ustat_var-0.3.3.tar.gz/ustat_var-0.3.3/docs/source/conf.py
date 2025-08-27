import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ustat_var'
copyright = '2025, Evan K. Rose, Jonathan T. Schellenberg, Yotam Shem-Tov, and Jack Mulqueeney'
author = 'Evan K. Rose, Jonathan T. Schellenberg, Yotam Shem-Tov, and Jack Mulqueeney'
release = '0.3.3'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx_copybutton',
    'sphinx.ext.mathjax',
]

autosummary_generate = True
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

templates_path = ['_templates']
exclude_patterns = []

html_static_path = ['_static']
def setup(app):
    app.add_css_file('custom.css')  # For Sphinx >= 1.8

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


# -- Options for HTML output
html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'
