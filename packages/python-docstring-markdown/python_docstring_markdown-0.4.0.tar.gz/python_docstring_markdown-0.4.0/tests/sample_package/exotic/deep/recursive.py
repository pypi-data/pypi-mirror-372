"""
A little recursive module using ReST-style docstrings.

This module demonstrates ReST-style docstrings with various utility functions.
"""

from typing import Any, Dict


class Serializable:
    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initialize a Serializable object.

        :param data: Data to serialize
        """
        self.data = data

    def serialize(self) -> Dict[str, Any]:
        """
        Serialize the object to a dictionary.

        Returns
        -------
        Dict[str, Any]
            Dictionary representation of the object
        """
        return self.data
