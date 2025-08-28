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
"""Record building utilities for converting between core and protobuf."""
from typing import Any, Dict, List, Sequence

from ayx_python_sdk.core.constants import NULL_VALUE_PLACEHOLDER
from ayx_python_sdk.core.field import FieldType
from ayx_python_sdk.core.metadata import Metadata
from ayx_python_sdk.providers.amp_provider.builders.packers import (
    _BlobPacker,
    _BoolFalsePacker,
    _BoolPacker,
    _BoolTruePacker,
    _BytePacker,
    _DatePacker,
    _DatetimePacker,
    _DoublePacker,
    _EmptyStringPacker,
    _FloatPacker,
    _IndirectBlobPacker,
    _IndirectStringPacker,
    _Int0Packer,
    _Int16Packer,
    _IntegerPacker,
    _LongIntegerPacker,
    _NullPacker,
    _Packer,
    _StringPacker,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.record_packet_pb2 import (
    AMPFieldType,
    Record as ProtobufRecord,
)


class RecordBuilder:
    """Utilities for converting records between protobuf and core format objects."""

    _field_type_to_packer: Dict[Any, _Packer] = {
        AMPFieldType.STRING: _StringPacker(),
        AMPFieldType.BLOB: _BlobPacker(),
        AMPFieldType.SPATIALOBJ: _BlobPacker(),
        AMPFieldType.BCD: _BlobPacker(),
        AMPFieldType.BOOL: _BoolPacker(),
        AMPFieldType.INT0: _Int0Packer(),
        AMPFieldType.UINT8: _BytePacker(),
        AMPFieldType.INT16: _Int16Packer(),
        AMPFieldType.INT32: _IntegerPacker(),
        AMPFieldType.INT64: _LongIntegerPacker(),
        AMPFieldType.FLOAT: _FloatPacker(),
        AMPFieldType.DOUBLE: _DoublePacker(),
        AMPFieldType.DATE: _DatePacker(),
        AMPFieldType.TIME: _IntegerPacker(),
        AMPFieldType.DATETIME: _DatetimePacker(),
        AMPFieldType.INDIRECTSTRING: _IndirectStringPacker(),
        AMPFieldType.INDIRECTBLOB: _IndirectBlobPacker(),
        AMPFieldType.INDIRECTSPATIAL: _IndirectBlobPacker(),
        AMPFieldType.BOOLFALSE: _BoolFalsePacker(),
        AMPFieldType.BOOLTRUE: _BoolTruePacker(),
        AMPFieldType.EMPTYSTRING: _EmptyStringPacker(),
        AMPFieldType.NULL: _NullPacker(),
    }

    _blob_cosmetic_types_to_amp_type = {
        FieldType.blob: AMPFieldType.BLOB,
        FieldType.spatialobj: AMPFieldType.SPATIALOBJ,
        FieldType.fixeddecimal: AMPFieldType.BCD,
    }

    _datetime_cosmetic_types_to_amp_type = {
        FieldType.date: AMPFieldType.DATE,
        FieldType.datetime: AMPFieldType.DATETIME,
        FieldType.time: AMPFieldType.TIME,
    }

    _float_cosmetic_types_to_amp_type = {
        FieldType.float: AMPFieldType.FLOAT,
        FieldType.double: AMPFieldType.DOUBLE,
    }

    _int_cosmetic_types_to_amp_type = {
        FieldType.byte: AMPFieldType.UINT8,
        FieldType.int16: AMPFieldType.INT16,
        FieldType.int32: AMPFieldType.INT32,
        FieldType.int64: AMPFieldType.INT64,
    }

    _null_values = {NULL_VALUE_PLACEHOLDER, None}

    @classmethod
    def from_protobuf(cls, record: ProtobufRecord) -> List:
        """
        Convert a protobuf to a list of values.

        Parameters
        ----------
        record
            Protobuf representation of a record.

        Returns
        -------
        List
            All elements of the record as a list.
        """
        start_byte_idx = 0
        parsed_record = []

        for amp_type in record.types:
            try:
                packer = cls._field_type_to_packer[amp_type]
            except KeyError:
                raise ValueError(f"Packer not found for type: {amp_type}")

            element, stride = packer.unpack(record.data, start_byte_idx)

            parsed_record.append(element)
            start_byte_idx += stride

        return parsed_record

    @classmethod
    def to_protobuf(cls, record: Sequence, metadata: Metadata) -> ProtobufRecord:
        """
        Convert a sequence of values to a protobuf.

        Parameters
        ----------
        record
            A sequence of values.
        metadata
            Metadata associated with the values.

        Returns
        -------
        ProtobufRecord
            The protobuf representation of the passed in record.
        """
        assert len(record) == len(metadata)

        raw_data = bytes()
        amp_types = []
        for field, element in zip(metadata, record):
            try:
                amp_type = cls._get_amp_type(field.type, element)
                packer = cls._field_type_to_packer[amp_type]
            except KeyError:
                raise ValueError(f"Packer not found for type: {field.type}")

            raw_data += packer.pack(element)
            amp_types.append(amp_type)

        return ProtobufRecord(data=raw_data, types=amp_types)

    @classmethod
    def _get_amp_type(cls, cosmetic_type: FieldType, element: Any) -> AMPFieldType:
        if element in cls._null_values:
            return AMPFieldType.NULL

        if cosmetic_type in [
            FieldType.string,
            FieldType.v_string,
            FieldType.v_wstring,
            FieldType.wstring,
        ]:
            if element == "":
                return AMPFieldType.EMPTYSTRING

            return AMPFieldType.STRING

        if cosmetic_type in cls._blob_cosmetic_types_to_amp_type:
            return cls._blob_cosmetic_types_to_amp_type[cosmetic_type]

        if cosmetic_type == FieldType.bool:
            if element:
                return AMPFieldType.BOOLTRUE

            return AMPFieldType.BOOLFALSE

        if element == 0:
            return AMPFieldType.INT0

        if cosmetic_type in cls._float_cosmetic_types_to_amp_type:
            return cls._float_cosmetic_types_to_amp_type[cosmetic_type]

        if cosmetic_type in cls._datetime_cosmetic_types_to_amp_type:
            return cls._datetime_cosmetic_types_to_amp_type[cosmetic_type]

        if cosmetic_type in cls._int_cosmetic_types_to_amp_type:
            return cls._int_cosmetic_types_to_amp_type[cosmetic_type]

        raise ValueError(
            f"AMP field type not found for cosmetic type {cosmetic_type} and value {element}."
        )
