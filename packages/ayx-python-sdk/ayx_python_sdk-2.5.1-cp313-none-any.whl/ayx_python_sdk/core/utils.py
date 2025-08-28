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
"""Utility functions definitions for plugin SDK."""

import datetime
from typing import Dict

from ayx_python_sdk.core.field import Field, FieldType

import pyarrow as pa


def to_date(stdate: str) -> "datetime.date":
    """Turn a date represented by a string to a Python date.

    (only the date part and not the time of the day)
    """
    return datetime.datetime.strptime(stdate, "%m/%d/%Y").date()


def to_time(sttime: str) -> "datetime.time":
    """Turn a date represented by a string to a Python time."""
    return datetime.datetime.strptime(sttime, "%H:%M:%S").time()


def to_datetime(stdatetime: str) -> "datetime.datetime":
    """Turn a date represented by a string to a Python datetime."""
    return datetime.datetime.strptime(stdatetime, "%m/%d/%Y %H:%M:%S")


def is_spatial(metadata: "pa.Metadata") -> bool:
    """Return true if the given arrow type is a spatial object (string + 'ayx' meta info)."""
    return metadata.get(b"ayx.source", None) == b"WKT"


def create_schema(col_meta: Dict = {}) -> "pa.Schema":
    """Create a Python Arrow Schema given a Dict of Metadata."""
    fields = []
    for name, data in col_meta.items():
        if isinstance(data, dict):
            fd = Field(
                name,
                field_type=data.get("type", FieldType.string),
                size=data.get("size", 0),
                scale=data.get("scale", 0),
                source=data.get("source", ""),
                description=data.get("description", ""),
            )
        else:
            fd = Field(name, data)
        fields.append(fd.to_arrow())
    return pa.schema(fields)


def get_ayx_meta(metaname: str) -> str:
    """Add ayx. prefix to metadata name."""
    if metaname in ["type", "size", "scale", "source", "description"]:
        return "ayx." + metaname
    raise ValueError("bad metadata name: " + metaname)


def set_metadata(
    tbl: "pa.Table", col_meta: Dict = {}, schema: "pa.Schema" = None
) -> "pa.Table":
    """Store column-level metadata as byte strings.

    Column-level metadata is stored in the table columns schema fields.

    To update the metadata, first new fields are created for all columns.
    Next a schema is created using the new fields and updated table metadata.
    Finally a new table is created by replacing the old one's schema, but
    without copying any data.

    Args:
    ----
        tbl (pyarrow.Table): The table to store metadata in
        col_meta: A dictionary with column metadata in the form
            {
                'column_1': {'type': FieldType.int64, 'size': 8},
                'column_2': {'size': 64, 'source': 'something'}
            }
    """
    # Create updated column fields with new metadata
    if schema:
        return pa.Table.from_arrays(list(tbl.itercolumns()), schema=schema)

    if col_meta:
        fields = []
        for col in tbl.schema:
            if col.name in col_meta:
                # Get updated column metadata
                metadata = col.metadata.copy() or {}
                for k, v in col_meta[col.name].items():
                    metadata[get_ayx_meta(k).encode("utf-8")] = str(v).encode("utf-8")
                # Update field with updated metadata
                col = pa.field(
                    col.name, col.type, nullable=col.nullable, metadata=metadata
                )
            fields.append(col)

        # Create new schema with updated field metadata
        schema = pa.schema(fields)

        # With updated schema build new table (shouldn't copy data)
        # tbl = pa.Table.from_batches(tbl.to_batches(), schema)
        tbl = pa.Table.from_arrays(list(tbl.itercolumns()), schema=schema)

    return tbl


def decode_metadata(metadata: Dict) -> Dict:
    """Arrow stores metadata keys and values as bytes."""
    if not metadata:
        # None or {} are not decoded
        return metadata

    decoded = {}
    for k, v in metadata.items():
        key = k.decode("utf-8")
        if key[0:4] == "ayx.":
            key = key[4:]
        val = v.decode("utf-8")
        decoded[key] = val
    return decoded


def get_metadata(tbl: "pa.Table", col_name: str = "") -> Dict:
    """Get all column metadata as dicts or just one column, given col_name."""
    if col_name:
        for col in tbl.schema:
            if col.name == col_name:
                return decode_metadata(col.metadata)
        return {}
    else:
        return {col.name: decode_metadata(col.metadata) for col in tbl.schema}
