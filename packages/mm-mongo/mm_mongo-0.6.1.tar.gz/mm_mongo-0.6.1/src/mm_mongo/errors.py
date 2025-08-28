"""
Custom exceptions for mm-mongo library.

This module defines MongoDB-specific exceptions that provide more context
and better error handling compared to generic exceptions.
"""


class MongoNotFoundError(Exception):
    """
    Raised when a MongoDB document is not found by ID.

    Attributes:
        id: The ID of the document that was not found
    """

    def __init__(self, id: object) -> None:
        """Initialize with the document ID that was not found."""
        self.id = id
        super().__init__(f"mongo document not found: {id}")
