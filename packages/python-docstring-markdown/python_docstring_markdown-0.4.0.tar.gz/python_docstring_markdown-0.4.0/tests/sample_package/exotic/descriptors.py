"""Descriptors and metaclasses demonstration.

This module shows how to use descriptors and metaclasses
with proper documentation.
"""


class ValidatedField:
    """A descriptor that validates its values.

    Parameters
    ----------
    validator : callable
        A function that takes a value and returns True if valid
    error_message : str
        Message to display when validation fails

    Examples
    --------
    >>> class User:
    ...     name = ValidatedField(lambda x: len(x) >= 3, "Name too short")
    """

    def __init__(self, validator, error_message):
        self.validator = validator
        self.error_message = error_message
        self.name = None

    def __get__(self, instance, owner):
        """Get the field value.

        Args:
            instance: The instance being accessed
            owner: The owner class

        Returns:
            The field value
        """
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        """Set and validate the field value.

        Args:
            instance: The instance being modified
            value: The new value to set

        Raises:
            ValueError: If the value fails validation
        """
        if not self.validator(value):
            raise ValueError(self.error_message)
        instance.__dict__[self.name] = value
