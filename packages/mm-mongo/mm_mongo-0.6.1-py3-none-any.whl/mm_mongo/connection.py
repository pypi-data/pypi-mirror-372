"""MongoDB connection classes for sync and async operations."""

from urllib.parse import urlparse

from pymongo import AsyncMongoClient, MongoClient, WriteConcern

from mm_mongo.types import DocumentType


class MongoConnection:
    """Synchronous MongoDB connection wrapper."""

    def __init__(self, url: str, tz_aware: bool = True, write_concern: WriteConcern | None = None) -> None:
        """
        Initialize sync MongoDB connection.

        Args:
            url: MongoDB connection URL with database name in path
            tz_aware: Whether to make datetime objects timezone-aware
            write_concern: Write concern for operations
        """
        self.client: MongoClient[DocumentType] = MongoClient(url, tz_aware=tz_aware)
        self.database = self.client.get_database(urlparse(url).path[1:], write_concern=write_concern)


class AsyncMongoConnection:
    """Asynchronous MongoDB connection wrapper."""

    def __init__(self, url: str, tz_aware: bool = True, write_concern: WriteConcern | None = None) -> None:
        """
        Initialize async MongoDB connection.

        Args:
            url: MongoDB connection URL with database name in path
            tz_aware: Whether to make datetime objects timezone-aware
            write_concern: Write concern for operations
        """
        self.client: AsyncMongoClient[DocumentType] = AsyncMongoClient(url, tz_aware=tz_aware)
        self.database = self.client.get_database(urlparse(url).path[1:], write_concern=write_concern)
