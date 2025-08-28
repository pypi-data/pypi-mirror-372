# Configuration file for the Sphinx documentation builder.

import os
import sys

# Add the parent directory (containing homodyne package) to Python path
sys.path.insert(0, os.path.abspath(".."))

# Also add the homodyne package directory itself
homodyne_path = os.path.join(os.path.abspath(".."), "homodyne")
if os.path.exists(homodyne_path):
    sys.path.insert(0, homodyne_path)

# -- Project information -----------------------------------------------------
project = "Homodyne Analysis"
copyright = "2025, Wei Chen, Hongrui He"
author = "Wei Chen, Hongrui He"
release = "0.6.6"
version = "0.6.6"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    # "sphinx.ext.autosummary",  # Disabled due to import issues with mocked modules
    "myst_parser",
]

# Suppress specific warnings to reduce noise
suppress_warnings = [
    "misc.highlighting_failure",
    "autosummary",
    "autodoc.import_object",
    "toc.not_included",
]

# Performance optimizations - mock heavy dependencies
autodoc_mock_imports = [
    "numba",
    "pymc",
    "arviz",
    "pytensor",
    "xpcs_viewer",
    "h5py",
    # Mock modules that don't exist but are referenced in docs
    "mcmc",  # This appears to be incorrectly referenced
    "io_utils",  # Missing module referenced in autosummary
    "kernels",  # Missing module referenced in autosummary
    "classical",  # Missing module referenced in autosummary
    "config",  # Missing module referenced in autosummary
    # Mock problematic homodyne submodules temporarily
    "homodyne.analysis",
    "homodyne.analysis.core",
    "homodyne.core",
    "homodyne.core.config",
    "homodyne.core.kernels",
    "homodyne.core.io_utils",
    "homodyne.optimization",
    "homodyne.optimization.mcmc",
    "homodyne.optimization.classical",
    "homodyne.plotting",
]
autodoc_preserve_defaults = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The default language to highlight source code in.
highlight_language = "python3"

# -- Options for extensions --------------------------------------------------

# autodoc configuration
autodoc_typehints = "description"
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "special-members": "__init__",
    "exclude-members": "__weakref__",
}

# Optimize autodoc performance
autodoc_class_signature = "mixed"
autodoc_inherit_docstrings = True
autodoc_typehints_format = "short"

# napoleon configuration
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
napoleon_type_aliases = None

# intersphinx configuration
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
}

# MyST parser configuration
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]

# Configure MyST parser for better performance
myst_heading_anchors = 2
myst_footnote_transition = True
myst_dmath_double_inline = True

# Add substitutions for common mathematical symbols
myst_substitutions = {
    "g1": r"$g_1$",
    "g2": r"$g_2$",
    "chi2": r"$\chi^2$",
    "alpha": r"$\alpha$",
    "beta": r"$\beta$",
    "gamma": r"$\gamma$",
}

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "analytics_id": "",
    "logo_only": False,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "style_nav_header_background": "#2980b9",
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 3,
    "includehidden": True,
    "titles_only": False,
}

# Optimize HTML output
html_copy_source = False
html_show_sourcelink = False
html_compact_lists = True
html_secnumber_suffix = ". "

html_static_path = ["_static"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# -- Options for LaTeX output ------------------------------------------------
latex_elements = {
    "papersize": "letterpaper",
    "pointsize": "10pt",
    "preamble": "",
    "fncychap": "\\usepackage[Bjornstrup]{fncychap}",
    "printindex": "\\footnotesize\\raggedright\\printindex",
}

latex_documents = [
    (
        "index",
        "homodyne-analysis.tex",
        "Homodyne Analysis Documentation",
        "Wei Chen, Hongrui He",
        "manual",
    ),
]

# -- Options for manual page output ------------------------------------------
man_pages = [
    ("index", "homodyne-analysis", "Homodyne Analysis Documentation", [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------
texinfo_documents = [
    (
        "index",
        "homodyne-analysis",
        "Homodyne Analysis Documentation",
        author,
        "homodyne-analysis",
        "One line description of project.",
        "Miscellaneous",
    ),
]
