import pytest
from pymongo import IndexModel

from mm_mongo.utils import parse_indexes, parse_sort, parse_str_index_model


def test_parse_indexes():
    # Test with list of strings
    assert [i.document for i in parse_indexes(["a"])] == [IndexModel("a").document]
    assert [i.document for i in parse_indexes(["a", "b"])] == [IndexModel("a").document, IndexModel("b").document]
    assert [i.document for i in parse_indexes(["a", "!b"])] == [IndexModel("a").document, IndexModel("b", unique=True).document]

    # Test compound indexes with colon syntax
    compound_result = parse_indexes(["f1", "!f2:-f3", "-f4"])
    assert len(compound_result) == 3
    assert compound_result[0].document == IndexModel("f1").document
    assert compound_result[1].document == IndexModel([("f2", 1), ("f3", -1)], unique=True).document
    assert compound_result[2].document == IndexModel([("f4", -1)]).document


def test_parse_str_index_model_validation():
    # Test valid formats
    assert IndexModel("k").document == parse_str_index_model("k").document
    assert IndexModel("k", unique=True).document == parse_str_index_model("!k").document
    assert IndexModel([("a", 1), ("b", -1)], unique=True).document == parse_str_index_model("!a:-b").document

    # Test invalid formats with commas

    with pytest.raises(ValueError, match="contains comma"):
        parse_str_index_model("a,b")

    with pytest.raises(ValueError, match="contains comma"):
        parse_str_index_model("!a,b")

    # Test invalid formats with spaces
    with pytest.raises(ValueError, match="contains spaces"):
        parse_str_index_model("a b")

    with pytest.raises(ValueError, match="contains spaces"):
        parse_str_index_model("!a :-b")


def test_parse_sort():
    assert parse_sort("a") == [("a", 1)]
    assert parse_sort("-a") == [("a", -1)]
    assert parse_sort("a,b") == [("a", 1), ("b", 1)]
    assert parse_sort("a, b") == [("a", 1), ("b", 1)]
    assert parse_sort("a,-b") == [("a", 1), ("b", -1)]
    assert parse_sort("-a,-b") == [("a", -1), ("b", -1)]
    assert parse_sort([("a", 1), ("b", -1)]) == [("a", 1), ("b", -1)]
    assert parse_sort(None) is None
