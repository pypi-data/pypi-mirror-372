import os
import sys
from datetime import datetime

import mater

sys.path.insert(0, os.path.abspath("../.."))

project = "MATER"
copyright = f"{datetime.now().year}, François Verzier"
author = "François Verzier"
release = str(mater.__version__)

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.napoleon",  # Handle Google/NumPy style docstrings
    "sphinxcontrib.bibtex",
    "sphinx_copybutton",
    "sphinx_design",
]

# BibTeX configuration (common for both builders)
bibtex_bibfiles = ["_static/biblio.bib"]
bibtex_default_style = "plain"
bibtex_reference_style = "author_year"

# MyST markdown extension
myst_enable_extensions = ["colon_fence"]

# Autodoc settings (common for both builders)
autodoc_typehints = "description"
autodoc_class_signature = "separated"

# Common static path
html_static_path = ["_static"]

# -- HTML-specific configuration ---------------------------------------------
html_logo = "_static/MATER_logo.png"

html_theme_options = {
    "show_version_warning_banner": True,
    "navbar_align": "left",
    "show_prev_next": False,
    "secondary_sidebar_items": ["page-toc", "edit-this-page", "sourcelink"],
    "show_toc_level": 4,
    "icon_links": [
        {
            "name": "Instagram",
            "icon": "fa-brands fa-instagram",
            "type": "fontawesome",
        },
        {
            "name": "GitLab",
            "url": "https://gricad-gitlab.univ-grenoble-alpes.fr/isterre-dynamic-modeling/mater-project/mater",
            "icon": "fa-brands fa-gitlab",
            "type": "fontawesome",
        },
        {
            "name": "Zenodo",
            "url": "https://zenodo.org/search?q=parent.id%3A12751420&f=allversions%3Atrue&l=list&p=1&s=10&sort=version",
            "icon": "_static/simple-icons--zenodo.svg",
            "type": "local",
        },
    ],
    "icon_links_label": "Quick Links",
}


# -- LaTeX-specific configuration --------------------------------------------
latex_elements = {
    "papersize": "a4paper",
    "pointsize": "10pt",
    "preamble": "",  # Clear any custom preamble
    "maketitle": "",  # Exclude Sphinx title page
    "tableofcontents": "",  # Exclude Sphinx-generated table of contents
}
# sd_fontawesome_latex = True
toc_object_entries_show_parents = "hide"

napoleon_google_docstring = False
napoleon_numpy_docstring = True

# # This setting ensures the method name becomes a section
# autodoc_member_order = "bysource"

html_theme = "pydata_sphinx_theme"  # pydata_sphinx_theme alabaster
# master_doc = "technical_reference/model/index"  # uncomment to generate the documentation only for a subsection
