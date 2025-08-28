from pymongo import ASCENDING, DESCENDING, IndexModel

from mm_mongo.types import SortType


def parse_sort(sort: SortType) -> list[tuple[str, int]] | None:
    if isinstance(sort, str):
        result = []
        for field in sort.split(","):
            field = field.strip()  # noqa: PLW2901
            if field.startswith("-"):
                result.append((field[1:], -1))
            else:
                result.append((field, 1))
        return result
    return sort


def parse_indexes(value: list[IndexModel | str]) -> list[IndexModel]:
    """Parse index definitions from a list.

    Supports:
    - Single field: "field" (ascending), "-field" (descending), "!field" (unique)
    - Compound index: "!field1:-field2:field3" (unique compound with colon separators)

    Args:
        value: List of IndexModel objects or string index definitions

    Returns:
        List of IndexModel objects

    Raises:
        ValueError: If string index contains invalid characters (commas or spaces)
    """
    return [parse_str_index_model(index) if isinstance(index, str) else index for index in value]


def parse_str_index_model(index: str) -> IndexModel:
    # Validate format - no commas or spaces allowed
    if "," in index:
        msg = f"Index string '{index}' contains comma. Use list format: ['field1', 'field2'] instead of 'field1,field2'"
        raise ValueError(msg)
    if " " in index:
        raise ValueError(f"Index string '{index}' contains spaces. Remove spaces from index definition")

    unique = index.startswith("!")
    index = index.removeprefix("!")
    if ":" in index:
        keys = []
        for i in index.split(":"):
            order = DESCENDING if i.startswith("-") else ASCENDING
            keys.append((i.removeprefix("-"), order))
    else:
        order = DESCENDING if index.startswith("-") else ASCENDING
        index = index.removeprefix("-")
        keys = [(index, order)]
    if unique:
        return IndexModel(keys, unique=True)
    return IndexModel(keys)
