import asyncio
from typing import ClassVar

import pytest
from bson import ObjectId
from pymongo.errors import WriteError

from mm_mongo import AsyncMongoCollection, MongoModel, MongoNotFoundError
from mm_mongo.types import AsyncDatabaseAny


async def test_init_collection(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_init_collection"
        name: str

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)
    await col.insert_one(Data(id=1, name="n1"))
    await col.insert_one(Data(id=2, name="n2"))
    assert await col.count({}) == 2


async def test_schema_validation(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        name: str
        value: int

        __collection__: str = "data__test_schema_validation"
        __validator__: ClassVar[dict[str, object]] = {
            "$jsonSchema": {"required": ["name", "value"], "properties": {"value": {"minimum": 10}}},
        }

    await async_database.drop_collection(Data.__collection__)
    await asyncio.sleep(2)  # without it `-n auto` doesn't work. It looks like drop_collection invokes a little bit later
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)
    await col.insert_one(Data(id=1, name="n1", value=100))
    with pytest.raises(WriteError):
        await col.update_one({"name": "n1"}, {"$set": {"value": 3}})


async def test_insert_one(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_insert_one"
        name: str

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)
    res = await col.insert_one(Data(id=1, name="n1"))
    assert res.inserted_id == 1
    assert await col.count({}) == 1
    assert (await col.get(1)).name == "n1"


async def test_insert_many(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_insert_many"
        name: str

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)
    docs = [Data(id=1, name="n1"), Data(id=2, name="n2")]
    res = await col.insert_many(docs)
    assert res.inserted_ids == [1, 2]
    assert await col.count({}) == 2
    assert (await col.get(1)).name == "n1"
    assert (await col.get(2)).name == "n2"


async def test_get_or_none(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_get_or_none"
        name: str

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)
    await col.insert_one(Data(id=1, name="n1"))

    result = await col.get_or_none(1)
    assert result is not None
    assert result.name == "n1"
    assert await col.get_or_none(2) is None


async def test_get(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_get"
        name: str

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)
    await col.insert_one(Data(id=1, name="n1"))

    assert (await col.get(1)).name == "n1"

    with pytest.raises(MongoNotFoundError):
        await col.get(2)


async def test_find(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_find"
        name: str

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)
    docs = [Data(id=1, name="n1"), Data(id=2, name="n2"), Data(id=3, name="n3")]
    await col.insert_many(docs)

    # Test find all documents
    results = await col.find({})
    assert len(results) == 3
    assert results[0].name == "n1"
    assert results[1].name == "n2"
    assert results[2].name == "n3"

    # Test find with query
    results = await col.find({"name": "n1"})
    assert len(results) == 1
    assert results[0].name == "n1"

    # Test find with sort
    results = await col.find({}, sort="name")
    assert len(results) == 3
    assert results[0].name == "n1"
    assert results[1].name == "n2"
    assert results[2].name == "n3"

    results = await col.find({}, sort="-name")
    assert len(results) == 3
    assert results[0].name == "n3"
    assert results[1].name == "n2"
    assert results[2].name == "n1"

    # Test find with limit
    results = await col.find({}, limit=2)
    assert len(results) == 2
    assert results[0].name == "n1"
    assert results[1].name == "n2"


async def test_find_one(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_find_one"
        name: str

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)
    docs = [Data(id=1, name="n1"), Data(id=2, name="n2"), Data(id=3, name="n3")]
    await col.insert_many(docs)

    # Test find one document
    result = await col.find_one({"name": "n1"})
    assert result is not None
    assert result.name == "n1"

    # Test find one document with sort
    result = await col.find_one({}, sort="name")
    assert result is not None
    assert result.name == "n1"

    result = await col.find_one({}, sort="-name")
    assert result is not None
    assert result.name == "n3"

    # Test find one document with no match
    result = await col.find_one({"name": "n4"})
    assert result is None


async def test_update_and_get(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_update_and_get"
        name: str
        value: int

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)
    await col.insert_one(Data(id=1, name="n1", value=10))

    # Test update and get
    updated_doc = await col.update_and_get(1, {"$set": {"value": 20}})
    assert updated_doc.value == 20

    # Test update and get with non-existing document
    with pytest.raises(MongoNotFoundError):
        await col.update_and_get(2, {"$set": {"value": 30}})


async def test_set_and_get(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_set_and_get"
        name: str
        value: int

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)
    await col.insert_one(Data(id=1, name="n1", value=10))

    # Test set and get
    updated_doc = await col.set_and_get(1, {"value": 20})
    assert updated_doc.value == 20

    # Test set and get with non-existing document
    with pytest.raises(MongoNotFoundError):
        await col.set_and_get(2, {"value": 30})


async def test_update(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_update"
        name: str
        value: int

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)
    await col.insert_one(Data(id=1, name="n1", value=10))

    # Test update existing document
    update_result = await col.update(1, {"$set": {"value": 20}})
    assert update_result.matched_count == 1
    assert update_result.modified_count == 1
    updated_doc = await col.get(1)
    assert updated_doc.value == 20

    # Test update non-existing document without upsert
    update_result = await col.update(2, {"$set": {"value": 30}})
    assert update_result.matched_count == 0
    assert update_result.modified_count == 0

    # Test update non-existing document with upsert
    update_result = await col.update(2, {"$set": {"value": 30, "name": "n2"}}, upsert=True)
    assert update_result.matched_count == 0
    assert update_result.upserted_id == 2
    upserted_doc = await col.get(2)
    assert upserted_doc.value == 30


async def test_set(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_set"
        name: str
        value: int

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)
    await col.insert_one(Data(id=1, name="n1", value=10))

    # Test set existing document
    update_result = await col.set(1, {"value": 20})
    assert update_result.matched_count == 1
    assert update_result.modified_count == 1
    updated_doc = await col.get(1)
    assert updated_doc.value == 20

    # Test set non-existing document without upsert
    update_result = await col.set(2, {"value": 30})
    assert update_result.matched_count == 0
    assert update_result.modified_count == 0

    # Test set non-existing document with upsert
    update_result = await col.set(2, {"value": 30, "name": "n2"}, upsert=True)
    assert update_result.matched_count == 0
    assert update_result.upserted_id == 2
    upserted_doc = await col.get(2)
    assert upserted_doc.value == 30
    assert upserted_doc.name == "n2"


async def test_set_and_push(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_set_and_push"
        name: str
        values: list[int]

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)
    await col.insert_one(Data(id=1, name="n1", values=[1, 2]))

    # Test set and push
    update_result = await col.set_and_push(1, {"name": "n2"}, {"values": 3})
    assert update_result.matched_count == 1
    assert update_result.modified_count == 1
    updated_doc = await col.get(1)
    assert updated_doc.name == "n2"
    assert updated_doc.values == [1, 2, 3]

    # Test set and push with non-existing document
    update_result = await col.set_and_push(2, {"name": "n3"}, {"values": 4})
    assert update_result.matched_count == 0
    assert update_result.modified_count == 0


async def test_update_one(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_update_one"
        name: str
        value: int

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)
    await col.insert_one(Data(id=1, name="n1", value=10))

    # Test update one existing document
    update_result = await col.update_one({"_id": 1}, {"$set": {"value": 20}})
    assert update_result.matched_count == 1
    assert update_result.modified_count == 1
    updated_doc = await col.get(1)
    assert updated_doc.value == 20

    # Test update one non-existing document without upsert
    update_result = await col.update_one({"_id": 2}, {"$set": {"value": 30}})
    assert update_result.matched_count == 0
    assert update_result.modified_count == 0

    # Test update one non-existing document with upsert
    update_result = await col.update_one({"_id": 2}, {"$set": {"value": 30, "name": "n2"}}, upsert=True)
    assert update_result.matched_count == 0
    assert update_result.upserted_id == 2
    upserted_doc = await col.get(2)
    assert upserted_doc.value == 30
    assert upserted_doc.name == "n2"


async def test_update_many(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[ObjectId]):
        __collection__: str = "data__test_update_many"
        name: str
        value: int

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[ObjectId, Data] = await AsyncMongoCollection.init(async_database, Data)
    id1, id2, id3 = ObjectId(), ObjectId(), ObjectId()
    docs = [
        Data(id=id1, name="n1", value=10),
        Data(id=id2, name="n2", value=20),
        Data(id=id3, name="n1", value=30),
    ]
    await col.insert_many(docs)

    # Test update many existing documents
    update_result = await col.update_many({"name": "n1"}, {"$set": {"value": 40}})
    assert update_result.matched_count == 2
    assert update_result.modified_count == 2
    assert (await col.get(id1)).value == 40
    assert (await col.get(id3)).value == 40

    # Test update many non-existing documents without upsert
    update_result = await col.update_many({"name": "n3"}, {"$set": {"value": 50}})
    assert update_result.matched_count == 0
    assert update_result.modified_count == 0

    # Test update many non-existing documents with upsert
    update_result = await col.update_many({"name": "n3"}, {"$set": {"value": 50, "name": "n3"}}, upsert=True)
    assert update_result.matched_count == 0
    assert update_result.upserted_id is not None
    # Ensure the id is of type ObjectId
    if not isinstance(update_result.upserted_id, ObjectId):
        pytest.fail(f"Expected ObjectId, got {type(update_result.upserted_id)}")
    upserted_doc = await col.get(update_result.upserted_id)
    assert upserted_doc.value == 50
    assert upserted_doc.name == "n3"


async def test_set_many(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_set_many"
        name: str
        value: int

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)
    docs = [
        Data(id=1, name="n1", value=10),
        Data(id=2, name="n2", value=20),
        Data(id=3, name="n1", value=30),
    ]
    await col.insert_many(docs)

    # Test set many existing documents
    update_result = await col.set_many({"name": "n1"}, {"value": 40})
    assert update_result.matched_count == 2
    assert update_result.modified_count == 2
    assert (await col.get(1)).value == 40
    assert (await col.get(3)).value == 40

    # Test set many non-existing documents
    update_result = await col.set_many({"name": "n3"}, {"value": 50})
    assert update_result.matched_count == 0
    assert update_result.modified_count == 0


async def test_delete_many(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_delete_many"
        name: str

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)
    docs = [Data(id=1, name="n1"), Data(id=2, name="n2"), Data(id=3, name="n1")]
    await col.insert_many(docs)

    # Test delete many existing documents
    delete_result = await col.delete_many({"name": "n1"})
    assert delete_result.deleted_count == 2
    assert await col.count({}) == 1
    assert await col.get_or_none(1) is None
    assert await col.get_or_none(3) is None
    assert (await col.get(2)).name == "n2"

    # Test delete many non-existing documents
    delete_result = await col.delete_many({"name": "n3"})
    assert delete_result.deleted_count == 0
    assert await col.count({}) == 1


async def test_delete_one(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_delete_one"
        name: str

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)
    docs = [Data(id=1, name="n1"), Data(id=2, name="n2"), Data(id=3, name="n1")]
    await col.insert_many(docs)

    # Test delete one existing document
    delete_result = await col.delete_one({"name": "n1"})
    assert delete_result.deleted_count == 1
    assert await col.count({}) == 2
    assert await col.get_or_none(1) is None or await col.get_or_none(3) is None

    # Test delete one non-existing document
    delete_result = await col.delete_one({"name": "n3"})
    assert delete_result.deleted_count == 0
    assert await col.count({}) == 2


async def test_delete(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_delete"
        name: str

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)
    docs = [Data(id=1, name="n1"), Data(id=2, name="n2"), Data(id=3, name="n3")]
    await col.insert_many(docs)

    # Test delete existing document
    delete_result = await col.delete(1)
    assert delete_result.deleted_count == 1
    assert await col.count({}) == 2
    assert await col.get_or_none(1) is None

    # Test delete non-existing document
    delete_result = await col.delete(4)
    assert delete_result.deleted_count == 0
    assert await col.count({}) == 2


async def test_count(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_count"
        name: str

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)
    docs = [Data(id=1, name="n1"), Data(id=2, name="n2"), Data(id=3, name="n1")]
    await col.insert_many(docs)

    # Test count all documents
    assert await col.count({}) == 3

    # Test count with query
    assert await col.count({"name": "n1"}) == 2
    assert await col.count({"name": "n2"}) == 1
    assert await col.count({"name": "n3"}) == 0


async def test_exists(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_exists"
        name: str

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)
    docs = [Data(id=1, name="n1"), Data(id=2, name="n2"), Data(id=3, name="n1")]
    await col.insert_many(docs)

    # Test exists with existing documents
    assert await col.exists({"name": "n1"}) is True
    assert await col.exists({"name": "n2"}) is True

    # Test exists with non-existing documents
    assert await col.exists({"name": "n3"}) is False


async def test_drop_collection(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_drop_collection"
        name: str

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)
    await col.insert_one(Data(id=1, name="n1"))
    assert await col.count({}) == 1

    # Test drop collection
    await col.drop_collection()
    assert await col.count({}) == 0
    assert Data.__collection__ not in await async_database.list_collection_names()


async def test_nested_document(async_database: AsyncDatabaseAny) -> None:
    class NestedData(MongoModel[ObjectId]):
        __collection__: str = "nested__test_nested_document"
        name: str

    class Data(MongoModel[int]):
        __collection__: str = "data__test_nested_document"
        name: str
        nested: NestedData

    await async_database.drop_collection(NestedData.__collection__)
    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)
    await col.insert_one(Data(id=1, name="n1", nested=NestedData(id=ObjectId(), name="n1")))

    # Test find nested document
    doc = await col.get(1)
    assert doc.nested.name == "n1"

    # Test update nested document
    await col.update(1, {"$set": {"nested.name": "n2"}})
    doc = await col.get(1)
    assert doc.nested.name == "n2"


async def test_push(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_push"
        name: str
        items: list[str]

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)

    # Insert initial document
    await col.insert_one(Data(id=1, name="test", items=[]))

    # Test push single item
    push_result = await col.push(1, {"items": "item1"})
    assert push_result.matched_count == 1
    assert push_result.modified_count == 1

    doc = await col.get(1)
    assert doc.items == ["item1"]

    # Test push multiple items
    await col.push(1, {"items": "item2"})
    await col.push(1, {"items": "item3"})

    doc = await col.get(1)
    assert doc.items == ["item1", "item2", "item3"]

    # Test push with non-existing document
    push_result = await col.push(2, {"items": "item1"})
    assert push_result.matched_count == 0
    assert push_result.modified_count == 0


async def test_pull(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_pull"
        name: str
        items: list[str]

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)

    # Insert initial document with items
    await col.insert_one(Data(id=1, name="test", items=["item1", "item2", "item3"]))

    # Test pull single item
    pull_result = await col.pull(1, {"items": "item2"})
    assert pull_result.matched_count == 1
    assert pull_result.modified_count == 1

    doc = await col.get(1)
    assert doc.items == ["item1", "item3"]

    # Test pull non-existing item
    pull_result = await col.pull(1, {"items": "item4"})
    assert pull_result.matched_count == 1
    assert pull_result.modified_count == 0

    doc = await col.get(1)
    assert doc.items == ["item1", "item3"]

    # Test pull with non-existing document
    pull_result = await col.pull(2, {"items": "item1"})
    assert pull_result.matched_count == 0
    assert pull_result.modified_count == 0


async def test_set_and_pull(async_database: AsyncDatabaseAny) -> None:
    class Data(MongoModel[int]):
        __collection__: str = "data__test_set_and_pull"
        name: str
        items: list[str]

    await async_database.drop_collection(Data.__collection__)
    col: AsyncMongoCollection[int, Data] = await AsyncMongoCollection.init(async_database, Data)

    # Insert initial document with items
    await col.insert_one(Data(id=1, name="old_name", items=["item1", "item2", "item3"]))

    # Test set and pull
    update_result = await col.set_and_pull(1, {"name": "new_name"}, {"items": "item2"})
    assert update_result.matched_count == 1
    assert update_result.modified_count == 1

    doc = await col.get(1)
    assert doc.name == "new_name"
    assert doc.items == ["item1", "item3"]

    # Test set and pull with non-existing document
    update_result = await col.set_and_pull(2, {"name": "new_name"}, {"items": "item1"})
    assert update_result.matched_count == 0
    assert update_result.modified_count == 0
