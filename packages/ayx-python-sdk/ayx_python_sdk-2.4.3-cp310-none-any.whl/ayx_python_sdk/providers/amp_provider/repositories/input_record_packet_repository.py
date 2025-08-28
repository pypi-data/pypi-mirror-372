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
"""Class that saves/retrieves input record packets."""
import logging
from typing import Dict, List, TYPE_CHECKING, Tuple

from ayx_python_sdk.core.input_connection_base import InputConnectionStatus
from ayx_python_sdk.providers.amp_provider.amp_record_packet import AMPRecordPacket
from ayx_python_sdk.providers.amp_provider.builders.record_packet_builder import (
    RecordPacketBuilder,
)
from ayx_python_sdk.providers.amp_provider.repositories.input_connection_repository import (
    InputConnectionRepository,
)
from ayx_python_sdk.providers.amp_provider.repositories.input_metadata_repository import (
    InputMetadataRepository,
)
from ayx_python_sdk.providers.amp_provider.repositories.singleton import Singleton


if TYPE_CHECKING:
    from ayx_python_sdk.core.metadata import Metadata
    from ayx_python_sdk.core.record_packet_base import RecordPacketBase
    from ayx_python_sdk.providers.amp_provider.resources.generated.record_packet_pb2 import (
        RecordPacket as ProtobufRecordPacket,
    )

    import pandas as pd  # noqa: F401

logger = logging.getLogger(__name__)


class UnfinishedRecordPacketException(Exception):
    """Exception to be raised to indicate that a record packet isn't ready to be returned."""

    pass


class EmptyRecordPacketRepositoryException(Exception):
    """Exception to be raised after the final record packet has been returned."""

    pass


class InputRecordPacketRepository(metaclass=Singleton):
    """Repository that stores input record packets."""

    _record_packet_builder = RecordPacketBuilder()
    _input_connection_repo = InputConnectionRepository()

    def __init__(self) -> None:
        """Initialize the input record packet repository."""
        self._record_packet_cache: Dict[
            str, Dict[str, Tuple["pd.DataFrame", "pd.DataFrame", int]]
        ] = {}
        self._records_list: Dict[str, Dict[str, List["pd.DataFrame"]]] = {}

    def push_record_packet(
        self, anchor_name: str, connection_name: str, record_packet: "RecordPacketBase"
    ) -> None:
        """Save a record packet."""
        logger.debug(
            "Saving record packet (%r) for anchor %s on connection %s",
            record_packet,
            anchor_name,
            connection_name,
        )
        self._records_list.setdefault(anchor_name, {})
        self._records_list[anchor_name].setdefault(connection_name, [])

        self._record_packet_cache.setdefault(anchor_name, {})

        self._records_list[anchor_name][connection_name].append(
            record_packet.to_dataframe()
        )

    def save_grpc_record_packet(
        self,
        anchor_name: str,
        connection_name: str,
        grpc_record_packet: "ProtobufRecordPacket",
        metadata: "Metadata",
    ) -> None:
        """Save a record packet from its protobuffer format."""
        record_packet, _, _ = self._record_packet_builder.from_protobuf(
            grpc_record_packet, metadata
        )
        self.push_record_packet(anchor_name, connection_name, record_packet)

    def _reshape_packets(
        self, anchor_name: str, connection_name: str
    ) -> Tuple["pd.DataFrame", "pd.DataFrame", int]:
        """
        Reshape packets based on number of requested rows.

        Concatenate record packets from the queue into a single dataframe,
        then return that dataframe and the number of record packets to remove from the queue.

        Parameters
        ----------
        anchor_name
            The name of the input anchor that the metadata is associated with.
        connection_name
            The name of the input connection that the metadata is associated with.

        Returns
        -------
        Tuple["pd.DataFrame", "pd.DataFrame", int]
            A tuple containing:
            Dataframe containing the correct number of packets,
            the remainder of the original dataframe, and
            number of packets to remove from internal queue
        """
        import numpy as np  # noqa: F811
        import pandas as pd  # noqa: F811

        if anchor_name not in self._records_list:
            raise ValueError(f"Anchor {anchor_name} not found in repository.")

        if connection_name not in self._records_list[anchor_name]:
            raise ValueError(
                f"Connection {connection_name} not found in repository for anchor {anchor_name}."
            )

        if connection_name in self._record_packet_cache[anchor_name]:
            return self._record_packet_cache[anchor_name][connection_name]

        max_packet_size = self._input_connection_repo.get_connection(
            anchor_name, connection_name
        ).max_packet_size

        if len(self._records_list[anchor_name][connection_name]) == 0:
            raise EmptyRecordPacketRepositoryException

        if max_packet_size is None:
            self._record_packet_cache[anchor_name][connection_name] = (
                pd.concat(self._records_list[anchor_name][connection_name]),
                pd.DataFrame(),
                len(self._records_list[anchor_name][connection_name]),
            )
            return self._record_packet_cache[anchor_name][connection_name]

        cumulative_lengths: np.ndarray = np.cumsum(
            [len(packet) for packet in self._records_list[anchor_name][connection_name]]
        )
        if (
            cumulative_lengths[-1] < max_packet_size
            and not InputConnectionRepository().get_connection_status(
                anchor_name, connection_name
            )
            == InputConnectionStatus.CLOSED
        ):
            raise UnfinishedRecordPacketException

        packets = [
            idx
            for idx, element in enumerate(cumulative_lengths)
            if element > max_packet_size and idx > 0
        ] + [len(cumulative_lengths)]
        num_packets_to_merge = packets[0]

        df = pd.concat(
            self._records_list[anchor_name][connection_name][:num_packets_to_merge]
        )
        right_size_dataframe = df.iloc[:max_packet_size]
        overflow_dataframe = df.iloc[max_packet_size:]
        self._record_packet_cache[anchor_name][connection_name] = (
            right_size_dataframe,
            overflow_dataframe,
            num_packets_to_merge,
        )
        return self._record_packet_cache[anchor_name][connection_name]

    def peek_record_packet(
        self, anchor_name: str, connection_name: str
    ) -> "RecordPacketBase":
        """
        Get the next record packet without popping from the queue.

        Parameters
        ----------
        anchor_name
            The name of the input anchor that the metadata is associated with.
        connection_name
            The name of the input connection that the metadata is associated with.

        Returns
        -------
        RecordPacketBase
            The AMPRecordPacket at the front of the internal queue.
        """
        self._record_packet_cache.setdefault(anchor_name, {})
        right_size_dataframe, _, _ = self._reshape_packets(anchor_name, connection_name)
        return AMPRecordPacket(
            InputMetadataRepository().get_metadata(anchor_name, connection_name),
            right_size_dataframe,
        )

    def pop_record_packet(
        self, anchor_name: str, connection_name: str
    ) -> "RecordPacketBase":
        """
        Retrieve record packet if there are enough records to meet the max packet size criteria.

        Parameters
        ----------
        anchor_name
            The name of the input anchor that the metadata is associated with.
        connection_name
            The name of the input connection that the metadata is associated with.

        Returns
        -------
        RecordPacketBase
            The AMPRecordPacket that was popped off the internal queue.
        """
        (
            right_size_dataframe,
            remainder_packet,
            packets_to_remove,
        ) = self._reshape_packets(anchor_name, connection_name)

        self._records_list[anchor_name][connection_name] = self._records_list[
            anchor_name
        ][connection_name][packets_to_remove:]
        if connection_name in self._record_packet_cache[anchor_name]:
            del self._record_packet_cache[anchor_name][connection_name]

        if not remainder_packet.empty:
            self._records_list[anchor_name][connection_name].insert(0, remainder_packet)

        return AMPRecordPacket(
            InputMetadataRepository().get_metadata(anchor_name, connection_name),
            right_size_dataframe,
        )

    def clear_repository(self) -> None:
        """Delete all data in the repository."""
        logger.debug("Clearing InputRecordPacketRepository")
        self._records_list = {}
        self._record_packet_cache = {}
