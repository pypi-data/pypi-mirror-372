"""Sample package for testing docstring to markdown conversion.

This package contains various Python constructs with different docstring formats
to test the python-docstring-markdown package.

Available modules:
    - core: Core functionality with Google-style docstrings
    - utils: Utility functions with ReST-style docstrings
    - models: Data models with Numpydoc-style docstrings
"""

__version__ = "0.1.0"
__all__ = ["core", "utils", "models"]

from . import core, models, utils
