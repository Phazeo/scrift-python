"""The published package metadata names only this repository on GitHub.

PyPI shows ``[project.urls]`` and every other metadata field on the package
page, and only a new release can change them. 0.2.2 shipped a ``Repository``
link to an organisation that does not exist; this test makes that impossible.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

_PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"
_THIS_REPOSITORY = "https://github.com/Phazeo/scrift-python"
_GITHUB_URL = re.compile(r"https?://(?:www\.)?github\.com/[^\s\"'<>)]*", re.IGNORECASE)


def _strings(value: object) -> list[str]:
    """Every string anywhere in a parsed TOML value."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [s for v in value.values() for s in _strings(v)]
    if isinstance(value, list):
        return [s for v in value for s in _strings(v)]
    return []


def _github_urls_in_metadata() -> list[str]:
    project = tomllib.loads(_PYPROJECT.read_text())["project"]
    return [m.group(0) for s in _strings(project) for m in _GITHUB_URL.finditer(s)]


def test_the_repository_link_is_this_repository() -> None:
    project = tomllib.loads(_PYPROJECT.read_text())["project"]
    assert project["urls"]["Repository"] == _THIS_REPOSITORY


def test_the_metadata_names_no_other_github_url() -> None:
    others = [
        url
        for url in _github_urls_in_metadata()
        if url.rstrip("/").removesuffix(".git") != _THIS_REPOSITORY
        and not url.startswith(_THIS_REPOSITORY + "/")
    ]
    assert not others, f"package metadata names other GitHub URLs: {others}"
