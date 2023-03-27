# sphinx configuration

project = "plone.app.event"
copyright = "2012, Plone Foundation"

extensions = [
    "sphinx.ext.doctest",
    "sphinx.ext.coverage",
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
]
master_doc = "index"

language = "en"

from pkg_resources import get_distribution  # noqa: E402


version = release = get_distribution(project).version
