# Configuration file for the Sphinx documentation builder.

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../src'))

# Mock imports for ReadTheDocs
autodoc_mock_imports = [
    'aiida',
    'aiida.orm',
    'aiida.engine',
    'aiida.plugins',
    'aiida.parsers',
    'aiida.calculations',
    'aiida.common',
    'numpy',
    'matplotlib',
    'pandas',
]

# -- Project information -----------------------------------------------------
project = 'AiiDA Fireball'
copyright = '2025, ValkScripter and mohamedmamlouk'
author = 'ValkScripter and mohamedmamlouk'

# The full version, including alpha/beta/rc tags
release = '1.0.0'
version = '1.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Source file suffixes
source_suffix = ['.rst', '.md']

# The master toctree document
master_doc = 'index'

# -- MyST Parser configuration -----------------------------------------------
myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_image",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]

# Disable linkify to avoid installation issues on ReadTheDocs
myst_linkify_fuzzy_links = False

# -- Options for HTML output ------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_theme_options = {
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'style_nav_header_background': '#2980B9',
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

html_title = f"{project} v{version}"
html_short_title = project

# Add custom CSS
html_css_files = []

# -- Extension configuration -------------------------------------------------

# autodoc
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

autodoc_typehints = 'description'
autodoc_typehints_description_target = 'documented'

# autosummary
autosummary_generate = True

# intersphinx
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'aiida': ('https://aiida.readthedocs.io/projects/aiida-core/en/latest/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
    'ase': ('https://wiki.fysik.dtu.dk/ase/', None),
}

# napoleon
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# myst
myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]

myst_heading_anchors = 3

# copybutton
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# todo
todo_include_todos = True
