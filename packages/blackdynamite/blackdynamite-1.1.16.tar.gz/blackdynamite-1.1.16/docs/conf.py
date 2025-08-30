# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'BlackDynamite'
copyright = '2023, Guillaumne Anciaux'
author = 'Guillaumne Anciaux'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.mathjax',
              'sphinx.ext.todo', 'autoapi.extension', 'sphinx_rtd_theme', 'myst_parser'
              ]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

autoapi_dirs = ['../BlackDynamite']
autoapi_options = ['members', 'undoc-members',
                   'show-inheritance', 'show-module-summary', 'special-members', 'imported-members']
