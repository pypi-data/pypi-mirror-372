from bson import ObjectId

from mm_mongo import MongoModel


def test_monkey_patch_object_id():
    class Data(MongoModel[ObjectId]):
        name: str
        __collection__: str = "data"

    id = ObjectId()
    data = Data(id=id, name="n1")
    assert data.model_dump() == {"_id": id, "name": "n1"}
    assert data.model_dump(mode="json") == {"_id": str(id), "name": "n1"}
