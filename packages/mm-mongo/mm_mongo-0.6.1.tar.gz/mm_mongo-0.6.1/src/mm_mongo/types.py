"""Type definitions and result classes for mm-mongo library."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from bson import ObjectId
from pydantic import BaseModel
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.database import Database
from pymongo.results import DeleteResult, InsertManyResult, InsertOneResult, UpdateResult

# Type aliases for common MongoDB types
type SortType = None | list[tuple[str, int]] | str
"""Sort specification: None, list of (field, direction) tuples, or string like 'field,-other'."""

type QueryType = Mapping[str, object]
"""MongoDB query filter as a mapping of field names to values."""

type IdType = str | int | ObjectId
"""Document ID type: string, integer, or ObjectId."""

type DocumentType = Mapping[str, Any]
"""MongoDB document as a mapping of field names to any values."""

type DatabaseAny = Database[DocumentType]
"""Sync MongoDB database with document type."""

type AsyncDatabaseAny = AsyncDatabase[DocumentType]
"""Async MongoDB database with document type."""


class MongoUpdateResult(BaseModel):
    """Result of an update operation."""

    acknowledged: bool
    matched_count: int
    modified_count: int
    upserted_id: IdType | None

    @staticmethod
    def from_result(result: UpdateResult) -> MongoUpdateResult:
        """Convert PyMongo UpdateResult to MongoUpdateResult."""
        return MongoUpdateResult(
            acknowledged=result.acknowledged,
            matched_count=result.matched_count,
            modified_count=result.modified_count,
            upserted_id=result.upserted_id,
        )


class MongoInsertOneResult(BaseModel):
    """Result of a single document insert operation."""

    acknowledged: bool
    inserted_id: IdType

    @staticmethod
    def from_result(result: InsertOneResult) -> MongoInsertOneResult:
        """Convert PyMongo InsertOneResult to MongoInsertOneResult."""
        return MongoInsertOneResult(acknowledged=result.acknowledged, inserted_id=result.inserted_id)


class MongoInsertManyResult(BaseModel):
    """Result of a multiple document insert operation."""

    acknowledged: bool
    inserted_ids: list[IdType]

    @staticmethod
    def from_result(result: InsertManyResult) -> MongoInsertManyResult:
        """Convert PyMongo InsertManyResult to MongoInsertManyResult."""
        return MongoInsertManyResult(acknowledged=result.acknowledged, inserted_ids=result.inserted_ids)


class MongoDeleteResult(BaseModel):
    """Result of a delete operation."""

    acknowledged: bool
    deleted_count: int

    @staticmethod
    def from_result(result: DeleteResult) -> MongoDeleteResult:
        """Convert PyMongo DeleteResult to MongoDeleteResult."""
        return MongoDeleteResult(acknowledged=result.acknowledged, deleted_count=result.deleted_count)
