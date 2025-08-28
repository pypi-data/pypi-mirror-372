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
"""Utility methods for common functionality."""
import AlteryxPythonSDK as Sdk

from ayx_python_sdk.core.field import Field, FieldType
from ayx_python_sdk.core.metadata import Metadata


def convert_record_info_to_metadata(record_info: Sdk.RecordInfo) -> Metadata:
    """Convert the RecordInfo to Core Metadata."""
    return Metadata(
        [
            Field(
                name=field.name,
                field_type=FieldType[str(field.type)],
                size=field.size,
                scale=field.scale,
                source=field.source,
                description=field.description,
            )
            for field in record_info
        ]
    )


def convert_metadata_to_record_info(
    metadata: Metadata, engine: Sdk.AlteryxEngine
) -> Sdk.RecordInfo:
    """Convert between the metadata object and a Python SDK RecordInfo object."""
    record_info = Sdk.RecordInfo(engine)

    for field in metadata:
        record_info.add_field(
            field_name=field.name,
            field_type=getattr(Sdk.FieldType, str(field.type.name)),
            size=field.size,
            scale=field.scale,
            source=field.source,
            description=field.description,
        )

    return record_info
