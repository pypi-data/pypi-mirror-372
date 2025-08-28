"""Base MongoDB document model with Pydantic integration."""

from __future__ import annotations

from collections.abc import Callable
from typing import ClassVar

from pydantic import BaseModel, model_serializer, model_validator
from pydantic_core.core_schema import SerializationInfo
from pymongo import IndexModel

from mm_mongo.types import IdType


class MongoModel[ID: IdType](BaseModel):
    """
    Base class for MongoDB document models.

    Automatically handles `_id` ↔ `id` field mapping and supports
    collection configuration, schema validation, and indexing.
    """

    id: ID

    __collection__: str
    """MongoDB collection name (required)."""

    __validator__: ClassVar[dict[str, object] | None] = None
    """Optional MongoDB schema validator using JSON Schema format."""

    __indexes__: ClassVar[list[IndexModel | str]] = []
    """
    Optional indexes to create on the collection.

    Formats:
    - Single field: "field" (ascending), "-field" (descending), "!field" (unique)
    - Compound index: "!field1:-field2:field3" (unique compound with colon separators)
    - List: ["field1", "!field2:-field3", "-field4"]
    - IndexModel objects for complex indexes
    """

    @model_serializer(mode="wrap")
    def serialize_model(self, serializer: Callable[[object], dict[str, object]], _info: SerializationInfo) -> dict[str, object]:
        """Convert `id` field to `_id` for MongoDB storage."""
        data = serializer(self)
        data = {"_id": data["id"]} | data
        del data["id"]
        return data

    @model_validator(mode="before")
    @classmethod
    def restore_id(cls, values: dict[str, object]) -> dict[str, object]:
        """Convert `_id` field to `id` when loading from MongoDB."""
        if isinstance(values, dict) and "_id" in values:
            values["id"] = values.pop("_id")
        return values
