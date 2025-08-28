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
"""Defines a class for record metadata."""

from copy import deepcopy
from typing import Any, Iterator, List, Optional

from ayx_python_sdk.core.field import Field, FieldType


class Metadata:
    """
    Record Metadata class.

    This metadata is received by input connections, and written to output anchors.
    A metadata object is a composition of ordered Field objects.
    """

    def __init__(self, fields: Optional[List[Field]] = None) -> None:
        """
        Instantiate the Record Metadata class.

        Parameters
        ----------
        fields
            A list of fields that make up the metadata object.
        """
        self.fields = fields or []

    def add_field(
        self,
        name: str,
        field_type: FieldType,
        size: int = 0,
        scale: int = 0,
        source: str = "",
        description: str = "",
    ) -> Field:
        """
        Add a field to the record metadata.

        Parameters
        ----------
        name
            The name of the field.
        field_type
            The type of data that the field represents.
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

        Returns
        -------
        Field
            The field that was added to the metadata.
        """
        field = Field(
            name=name,
            field_type=field_type,
            size=size,
            scale=scale,
            source=source,
            description=description,
        )

        self.fields.append(field)
        return field

    def clone(self) -> "Metadata":
        """
        Make a deep copy of the record info.

        Returns
        -------
        Metadata
            A copy of this metadata object.
        """
        return deepcopy(self)

    def __len__(self) -> int:
        """
        Get the number of fields in the metadata.

        Returns
        -------
        int
            The number of fields in the metadata object.
        """
        return len(self.fields)

    def __iter__(self) -> Iterator[Field]:
        """
        Iterate over the fields in the metadata.

        Yields
        ------
        Field
            Each field in the metadata object.
        """
        yield from self.fields

    def __eq__(self, other: Any) -> bool:
        """
        Determine if metadata object is equivalent to another.

        Parameters
        ----------
        other
            The object to compare against.

        Returns
        -------
        bool
            Boolean value that indicates if the 2 objects are equal.
        """
        if not isinstance(other, Metadata):
            return NotImplemented
        if len(self) != len(other):
            return False
        return all([field == other_field for field, other_field in zip(self, other)])

    def __getitem__(self, item: int) -> Field:
        """
        Get the field at an index.

        Parameters
        ----------
        item
            The index of the field to get.

        Returns
        -------
        Field
            The field at the specified index.
        """
        if not isinstance(item, int):
            raise ValueError("Index must be integer.")
        if item < 0:
            raise ValueError("Index must be greater than 0.")
        if len(self.fields) < item:
            raise ValueError("Index out of bounds!")
        return self.fields[item]

    def __repr__(self) -> str:
        """
        Get the string representation of the object.

        Returns
        -------
        str
            The string representation of the metadata.
        """
        fields_str = "".join(["\n    " + repr(field) + "," for field in self]) + "\n"
        return f"Metadata({fields_str})"
