"""Utility functions module using ReST-style docstrings.

This module demonstrates ReST-style docstrings with various utility functions.
"""

import json
from typing import Any, Dict, List


def load_json(filepath: str) -> Dict[str, Any]:
    """Load and parse a JSON file.

    :param filepath: Path to the JSON file
    :type filepath: str
    :returns: Parsed JSON content as a dictionary
    :rtype: dict
    :raises FileNotFoundError: If the file doesn't exist
    :raises json.JSONDecodeError: If the file contains invalid JSON
    """
    with open(filepath, "r") as f:
        return json.loads(f.read())


def validate_data(data: Any, schema: Dict[str, Any]) -> List[str]:
    """Validate data against a schema.

    This function demonstrates multi-paragraph ReST docstrings.

    The schema should be a dictionary defining the expected structure
    and types of the data.

    :param data: Data to validate
    :param schema: Schema to validate against
    :returns: List of validation errors, empty if valid
    """
    # Placeholder implementation
    return []


class ValidationError(Exception):
    """Custom exception for validation errors.

    :param message: Error message
    :param errors: List of specific validation errors

    Example::

        raise ValidationError("Invalid data", ["field1 is required"])
    """

    def __init__(self, message: str, errors: List[str]):
        """Initialize ValidationError.

        :param message: Error message
        :param errors: List of validation errors
        """
        super().__init__(message)
        self.errors = errors
