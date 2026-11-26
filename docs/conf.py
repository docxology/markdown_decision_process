from pathlib import Path
import sys
from datetime import datetime

# Add the project source directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

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
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx_markdown_tables',
    'myst_parser',
]

# Add any paths that contain templates here
root_doc = 'index'

# List of patterns to exclude from source
exclude_patterns = ['_build', 'archive', 'manuscript', 'render-assets', 'AGENTS.md', 'README.md', 'Thumbs.db', '.DS_Store']

# The theme to use for HTML and HTML Help pages
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files


# Theme options
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False,
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