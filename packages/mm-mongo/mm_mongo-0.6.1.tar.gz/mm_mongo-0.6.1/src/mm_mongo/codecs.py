"""BSON codecs for custom type encoding/decoding."""

from decimal import Decimal
from typing import Any, no_type_check

from bson import Decimal128
from bson.codec_options import CodecOptions, TypeCodec, TypeRegistry


class DecimalCodec(TypeCodec):
    """Codec for converting between Python Decimal and BSON Decimal128."""

    python_type = Decimal
    bson_type = Decimal128

    @no_type_check
    def transform_python(self, value):  # noqa: ANN001, ANN201
        """Convert Python Decimal to BSON Decimal128."""
        return Decimal128(value)

    @no_type_check
    def transform_bson(self, value):  # noqa: ANN001, ANN201
        """Convert BSON Decimal128 to Python Decimal."""
        return value.to_decimal()


codec_options: CodecOptions[Any] = CodecOptions(type_registry=TypeRegistry([DecimalCodec()]), tz_aware=True)
"""Default codec options with Decimal support and timezone awareness."""
