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
"""Record packet building utilities for converting between core and protobuf."""
from typing import List, Tuple

from ayx_python_sdk.core.constants import NULL_VALUE_PLACEHOLDER
from ayx_python_sdk.core.metadata import Metadata
from ayx_python_sdk.core.record_packet_base import RecordPacketBase
from ayx_python_sdk.providers.amp_provider.amp_record_packet import AMPRecordPacket
from ayx_python_sdk.providers.amp_provider.builders.record_builder import RecordBuilder
from ayx_python_sdk.providers.amp_provider.resources.generated.record_packet_pb2 import (
    RecordPacket as ProtobufRecordPacket,
)


class RecordPacketBuilder:
    """Utilities for converting record packets between protobuf and core objects."""

    record_builder = RecordBuilder()

    @classmethod
    def from_protobuf(
        cls, protobuf_record_packet: ProtobufRecordPacket, metadata: Metadata
    ) -> Tuple[RecordPacketBase, int, float]:
        """
        Convert a protobuf to a record packet.

        Parameters
        ----------
        protobuf_record_packet
            Protobuf representation of a record packet.
        metadata
            Metadata associated with the record packet.

        Returns
        -------
        Tuple[RecordPacketBase, int, float]
            AMPRecordPacket representation of the protobuf record packet, sequence, and progress
        """
        import pandas as pd

        parsed_records = [
            cls.record_builder.from_protobuf(protobuf_record)
            for protobuf_record in protobuf_record_packet.records
        ]

        return (
            AMPRecordPacket(
                metadata=metadata,
                df=pd.DataFrame(
                    parsed_records, columns=[field.name for field in metadata]
                ),
            ),
            protobuf_record_packet.sequence,
            protobuf_record_packet.progress,
        )

    @classmethod
    def to_protobuf(
        cls, amp_record_packet: RecordPacketBase, sequence: int, progress: float
    ) -> List["ProtobufRecordPacket"]:
        """
        Convert a record packet to a protobuf.

        Parameters
        ----------
        amp_record_packet
            Protobuf representation of a record packet.
        sequence
            Position that the current record packet would be in,
            out of all record packets. (First, second, third, etc.)
        progress
            Overall progress (ranging from 0.0 to 1.0)

        Returns
        -------
        List[ProtobufRecordPacket]
            A list of ProtobufRecordPackets. If the passed in AMPRecordPacket would surpass 64MB,
            then there will be more than one element in list
        """
        df = amp_record_packet.to_dataframe()
        df.fillna(NULL_VALUE_PLACEHOLDER, inplace=True)

        metadata = amp_record_packet.metadata

        protobuf_records = [
            cls.record_builder.to_protobuf(record, metadata)
            for record in df.itertuples(index=False)
        ]

        size_limit = 64 * (2**20)  # 64 MB
        curr_size = 0

        pb_record_packets = []
        current_records = []

        for record in protobuf_records:
            record_size = len(record.data)
            if curr_size + record_size > size_limit:
                pb_record_packets.append(
                    ProtobufRecordPacket(
                        sequence=sequence,
                        progress=progress,
                        records=current_records,
                    )
                )
                sequence += 1
                current_records = []
                curr_size = 0

            current_records.append(record)
            curr_size += record_size

        if current_records:
            pb_record_packets.append(
                ProtobufRecordPacket(
                    sequence=sequence,
                    progress=progress,
                    records=current_records,
                )
            )
        return pb_record_packets
