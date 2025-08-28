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
"""Class that implements the serialization/deserialization for Metadata protobuf objects."""
import logging

from ayx_python_sdk.core.field import FieldType
from ayx_python_sdk.core.metadata import Metadata
from ayx_python_sdk.providers.amp_provider.resources.generated.metadata_pb2 import (
    FieldType as ProtobufFieldType,
    Metadata as ProtobufMetadata,
)

_protobuf_to_core_field_type = {
    "FT_BOOL": FieldType.bool.value,
    "FT_BYTE": FieldType.byte.value,
    "FT_INT16": FieldType.int16.value,
    "FT_INT32": FieldType.int32.value,
    "FT_INT64": FieldType.int64.value,
    "FT_FIXED_DECIMAL": FieldType.fixeddecimal.value,
    "FT_FLOAT": FieldType.float.value,
    "FT_DOUBLE": FieldType.double.value,
    "FT_STRING": FieldType.string.value,
    "FT_WSTRING": FieldType.wstring.value,
    "FT_V_STRING": FieldType.v_string.value,
    "FT_V_WSTRING": FieldType.v_wstring.value,
    "FT_DATE": FieldType.date.value,
    "FT_TIME": FieldType.time.value,
    "FT_DATETIME": FieldType.datetime.value,
    "FT_BLOB": FieldType.blob.value,
    "FT_SPATIALOBJ": FieldType.spatialobj.value,
}

_core_to_protobuf_field_type = {
    core_name: protobuf_name
    for protobuf_name, core_name in _protobuf_to_core_field_type.items()
}


logger = logging.getLogger(__name__)


class MetadataBuilder:
    """RPC Builder for transforming Metadata into Protobufs and vice versa."""

    @staticmethod
    def to_protobuf(amp_metadata: Metadata) -> ProtobufMetadata:
        """
        Serialize a Metadata (core.metadata) object into a protobuf.

        Parameters
        ----------
        amp_metadata
            AMP Metadata object to be serialized into protobuf.

        Returns
        -------
        ProtobufMetadata
            The Protobuf representation of the AMP Metadata object.
        """
        protobuf_metadata = ProtobufMetadata()
        for field in amp_metadata.fields:
            logger.debug("Serializing metadata field %s", field)
            f = protobuf_metadata.fields.add()
            f.name = field.name
            f.size = field.size
            f.scale = field.scale
            f.source = field.source
            f.description = field.description
            f.type = ProtobufFieldType.Value(
                _core_to_protobuf_field_type[field.type.value]
            )
        return protobuf_metadata

    @staticmethod
    def from_protobuf(protobuf_metadata: ProtobufMetadata) -> Metadata:
        """
        Deserialize a protobuf into a Metadata object (core.metadata).

        Parameters
        ----------
        protobuf_metadata
            Protobuf object to be serialized into an AMP metadata.

        Returns
        -------
        Metadata
            The AMP Metadata representation of the protobuf object.
        """
        amp_metadata = Metadata()
        for field in protobuf_metadata.fields:
            name = field.name
            field_type = FieldType(
                _protobuf_to_core_field_type[ProtobufFieldType.Name(field.type)]
            )
            size = field.size or 0
            scale = field.scale or 0
            source = field.source or ""
            description = field.description or ""
            amp_metadata.add_field(
                name=name,
                field_type=field_type,
                size=size,
                scale=scale,
                source=source,
                description=description,
            )
        return amp_metadata
