from __future__ import annotations

"""Top-level package for wspr-ai-lite utilities.

Version is sourced from pyproject.toml via distribution metadata at runtime.
"""

from importlib.metadata import PackageNotFoundError, version as _version

__all__ = ["__version__"]
try:
    __version__ = _version("wspr-ai-lite")
except PackageNotFoundError:  # e.g., editable dev before metadata exists
    __version__ = "0.0.0+dev"
