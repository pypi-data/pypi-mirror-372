"""
Fabricate Client - The official Fabricate client for Python.
"""

from .client import generate
try:
    import tomllib
except ImportError:
    import tomli as tomllib
from pathlib import Path

# Read version from pyproject.toml
_pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
with open(_pyproject_path, "rb") as f:
    _pyproject = tomllib.load(f)
    __version__ = _pyproject["project"]["version"]

__all__ = ["generate"] 