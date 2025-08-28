import os
import sys
import tomllib


# Project version (from pyproject.toml)
with open(os.path.abspath("../pyproject.toml"), "rb") as _f:
    _pyproject = tomllib.load(_f)

_project_table = _pyproject.get("project")
if not _project_table:
    raise ValueError("[project] table is missing in pyproject.toml")

_project_name = _project_table.get("name")
if not _project_name:
    raise ValueError("project.name is not set in pyproject.toml")

_project_version = _project_table.get("version")
if not _project_version:
    raise ValueError("project.version is not set in pyproject.toml")
if len(_project_version.split(".")) < 2:
    raise ValueError(f"project.version {_project_version} doesn't seem to be a valid semantic version")

project = _project_name.capitalize()
release = _project_version
version = ".".join(_project_version.split(".")[:2])

print(f"Project: {project}, Release: {release}, Version: {version}")

# Ensure project sources are importable
sys.path.insert(0, os.path.abspath("../src"))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
]

autosummary_generate = True
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

html_theme = "python_docs_theme"
templates_path = ["_templates"]
exclude_patterns = []
html_static_path = []

# Show version in the HTML title
html_title = f"{project} {release}"


rst_epilog = f"""
.. |project| replace:: {project}
.. |version| replace:: {version}
.. |release| replace:: {release}
"""
