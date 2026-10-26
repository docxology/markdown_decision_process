import os
import sys
from datetime import datetime

# Add the project source directory to the path
sys.path.insert(0, os.path.abspath('../src'))

# Project information
project = 'Markdown Decision Process'
copyright = f'{datetime.now().year}, MDP Contributors'
author = 'MDP Contributors'

# The full version, including alpha/beta/rc tags
release = '0.3.0'

# Add any Sphinx extension module names here
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx_markdown_tables',
    'myst_parser',
]

# Add any paths that contain templates here
templates_path = ['_templates']

# List of patterns to exclude from source
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The theme to use for HTML and HTML Help pages
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files
html_static_path = ['_static']

# Theme options
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False,
}

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'networkx': ('https://networkx.org/documentation/stable/', None),
}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False

# MyST parser settings
myst_enable_extensions = [
    'colon_fence',
    'deflist',
]

# Setup for versioned docs
version = release 