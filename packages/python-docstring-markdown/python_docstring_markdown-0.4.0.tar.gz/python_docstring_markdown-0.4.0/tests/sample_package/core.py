"""Core functionality module using Google-style docstrings.

This module demonstrates Google-style docstrings with various Python constructs
including nested classes, methods, and functions.
"""

from typing import Any, Dict, List, Optional


class DataProcessor:
    """Main data processing class.

    This class demonstrates nested class definitions and various method types.

    Attributes:
        name: The name of the processor
        config: Configuration dictionary
    """

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the DataProcessor.

        Args:
            name: Name of the processor
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}

    class Config:
        """Nested configuration class.

        This demonstrates nested class documentation.
        """

        def __init__(self):
            """Initialize Config object."""
            self.settings = {}

        def update(self, settings: Dict[str, Any]) -> None:
            """Update configuration settings.

            Args:
                settings: Dictionary of settings to update
            """
            self.settings.update(settings)

    def process(self, data: List[Any]) -> List[Any]:
        """Process the input data.

        Args:
            data: List of data items to process

        Returns:
            Processed data items

        Raises:
            ValueError: If data is empty
        """
        if not data:
            raise ValueError("Data cannot be empty")

        return [self._transform(item) for item in data]

    def _transform(self, item: Any) -> Any:
        """Internal method to transform a single item.

        Args:
            item: Item to transform

        Returns:
            Transformed item
        """
        return item


def batch_process(processor: DataProcessor, items: List[Any]) -> Dict[str, List[Any]]:
    """Batch process items using a DataProcessor.

    This is a module-level function demonstrating Google-style docstrings.

    Args:
        processor: DataProcessor instance to use
        items: List of items to process

    Returns:
        Dictionary containing:
            - 'processed': List of processed items
            - 'errors': List of items that failed processing
    """
    results = {"processed": [], "errors": []}

    for item in items:
        try:
            processed = processor.process([item])
            results["processed"].extend(processed)
        except Exception as e:
            results["errors"].append((item, str(e)))

    return results
