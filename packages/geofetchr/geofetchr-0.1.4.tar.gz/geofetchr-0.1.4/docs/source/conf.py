# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'geofetchr'
copyright = '2025, maruf islam'
author = 'maruf islam'
release = '0.1.4'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",    # auto-generate docs from docstrings
    "sphinx.ext.napoleon",   # support for Google/NumPy docstrings
    "sphinx.ext.viewcode",   # add links to highlighted source code
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'nature'
html_static_path = ['_static']
html_theme_options = {
    'description': 'GeoFetchr Documentation',
    'github_user': 'Maaruuuf',
    'github_repo': 'geofetchr',
    'fixed_sidebar': True,
}

