# Copyright (C) 2022 Alteryx, Inc. All rights reserved.
#
# Licensed under the ALTERYX SDK AND API LICENSE AGREEMENT;
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.alteryx.com/alteryx-sdk-and-api-license-agreement
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Record Field class definition."""
from enum import Enum
from typing import Any, Optional

import pyarrow as pa


class FieldType(Enum):
    """
    Field types.

    See AyxData/include/AyxData/dc/common/FieldType.h C++ enumeration.
    """

    bool = 1
    byte = 2
    int16 = 3
    int32 = 4
    int64 = 5
    fixeddecimal = 6
    float = 7
    double = 8
    string = 9
    wstring = 10
    v_string = 11
    v_wstring = 12
    date = 13
    time = 14
    datetime = 15
    blob = 16
    spatialobj = 17


class Field:
    """A record field that contains metadata like field name."""

    def __init__(
        self,
        name: str,
        field_type: FieldType,
        size: int = 0,
        scale: int = 0,
        source: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        Instantiate a field.

        Parameters
        ----------
        name
            The name of the field.
        field_type
            The type of data that this field represents.
        size
            The size of the data.

            For strings, this is the maximum number of characters.
            For blobs, this is the maximum number of bytes.
        scale
            The scale of the data. This only applies to fixeddecimal type.
        source
            The source of the data.
        description
            A description about the data that lives in this field.
        """
        # set maximum size for strings
        if size == 0:
            if field_type == FieldType.string or field_type == FieldType.wstring:
                size = 0x3FFF
            elif field_type == FieldType.v_string or field_type == FieldType.v_wstring:
                size = 0x7FFFFFFF
        if field_type == FieldType.spatialobj:
            source = "WKT"
        self.name = name
        self.type = field_type
        self.size = size
        self.scale = scale
        self.source = source or ""
        self.description = description or ""

    def __eq__(self, other: Any) -> bool:
        """
        Determine if 2 fields are equal.

        Parameters
        ----------
        other
            Any other object to compare against.

        Returns
        -------
        bool
            True if all properties of this field match the other field.
        """
        if not isinstance(other, Field):
            return NotImplemented
        return (
            self.name == other.name
            and self.type == other.type
            and self.size == other.size
            and self.scale == other.scale
            and self.source == other.source
            and self.description == other.description
        )

    def __repr__(self) -> str:
        """
        Get the string representation of the object.

        Returns
        -------
        str
            The string representation of the metadata.
        """
        return (
            f"Field(name={self.name}, field_type={self.type}, size={self.size}, "
            f'scale={self.scale}, source="{self.source}", description="{self.description}")'
        )

    def arrow_type(self) -> "pa.Type":
        """Return the Python Arrow type of this field."""
        if self.type == FieldType.bool:
            return pa.bool_()
        elif self.type == FieldType.byte:
            return pa.uint8()
        elif self.type == FieldType.int16:
            return pa.int16()
        elif self.type == FieldType.int32:
            return pa.int32()
        elif self.type == FieldType.int64:
            return pa.int64()
        elif self.type == FieldType.fixeddecimal:
            return pa.decimal256(76, 36)
        elif self.type == FieldType.float:
            return pa.float32()
        elif self.type == FieldType.double:
            return pa.float64()
        elif (
            self.type == FieldType.string
            or self.type == FieldType.wstring
            or self.type == FieldType.v_string
            or self.type == FieldType.v_wstring
        ):
            return pa.string()
        elif self.type == FieldType.date:
            return pa.date32()
        elif self.type == FieldType.time:
            return pa.time64("us")
        elif self.type == FieldType.datetime:
            return pa.date64()
        elif self.type == FieldType.blob:
            return pa.binary()
        elif self.type == FieldType.spatialobj:
            return pa.string()

    def to_arrow(self) -> "pa.Field":
        """Turn this Field to a Python Arrow Field."""
        return pa.field(self.name, self.arrow_type(), metadata=self.as_arrow_metadata())

    def as_arrow_metadata(self) -> dict:
        """Return dict representation of the field using ayx keys."""
        return {
            b"ayx.type": str(self.type.value).encode("utf-8"),
            b"ayx.size": str(self.size).encode("utf-8"),
            b"ayx.name": self.name.encode("utf-8"),
            b"ayx.scale": str(self.scale).encode("utf-8"),
            b"ayx.source": self.source.encode("utf-8"),
            b"ayx.description": self.description.encode("utf-8"),
        }
