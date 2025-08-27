import sys
import tomllib
from pathlib import Path

root_folder =  Path(__file__).parents[2]
sys.path.append(root_folder.joinpath("src"))

def parse_pyproject(root_path: Path) -> dict:
    """Parse the pyproject.toml file to extract project metadata.

    Parameters
    ----------
    root_path : Path
        The root path of the project containing the pyproject.toml file.

    Returns
    -------
    dict
        Dictionary containing the project metadata from the pyproject.toml file.

    Raises
    ------
    ValueError
        If the pyproject.toml file doesn't contain a project section.
    FileNotFoundError
        If the pyproject.toml file doesn't exist.
    """
    pyproject_path = root_path.joinpath("pyproject.toml")
    with pyproject_path.open("rb") as tml_file:
        toml_content = tomllib.load(tml_file)
    project: dict | None = toml_content.get("project")
    if project is None:
        raise ValueError(f"Compile the pyproject.toml in {root_path}")

    return project
    

pyproject_toml = parse_pyproject(root_folder)

project: str = pyproject_toml.get("name", "")
author: str = ", ".join(
    [author.get("name", "") for author in pyproject_toml.get("authors", [{}])]
)
copyright: str = f"2025, {author}"
release: str = pyproject_toml.get("version", "0.0.1")

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ["_templates"]
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
