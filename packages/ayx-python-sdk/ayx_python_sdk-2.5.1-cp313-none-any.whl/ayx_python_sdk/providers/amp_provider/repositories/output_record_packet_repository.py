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
"""Class that saves/retrieves output record packets."""
import logging
from typing import Dict, List, TYPE_CHECKING

from ayx_python_sdk.providers.amp_provider.builders import RecordPacketBuilder
from ayx_python_sdk.providers.amp_provider.repositories.grpc_repository import (
    GrpcRepository,
)
from ayx_python_sdk.providers.amp_provider.repositories.singleton import Singleton
from ayx_python_sdk.providers.amp_provider.resources.generated.outgoing_record_packet_push_pb2 import (
    OutgoingRecordPacketPush,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.record_packet_pb2 import (
    RecordPacket as ProtobufRecordPacket,
)

if TYPE_CHECKING:
    from ayx_python_sdk.core.record_packet_base import RecordPacketBase

logger = logging.getLogger(__name__)


class OutputRecordPacketRepository(metaclass=Singleton):
    """Repository that stores output record packets."""

    _record_packet_builder = RecordPacketBuilder()

    def __init__(self) -> None:
        """Initialize the output record packet repository."""
        self._record_packet_map: Dict[str, "RecordPacketBase"] = {}
        self._record_packet_sequence: Dict[str, int] = {}
        self._anchor_progress: Dict[str, float] = {}

    def save_record_packet(
        self, anchor_name: str, record_packet: "RecordPacketBase"
    ) -> None:
        """
        Save a record packet.

        Parameters
        ----------
        anchor_name
            The name of the anchor that the record packet is associated with.
        record_packet
            The record packet to save to the repository.
        """
        logger.debug(
            "Saving record packet for %s in OutputRecordPacketRepository", anchor_name
        )
        self._record_packet_map[anchor_name] = record_packet
        logger.debug(
            "Current OutputRecordPacketRepository State: %r", self._record_packet_map
        )

        try:
            client = GrpcRepository().get_sdk_engine_client()
        except ValueError:
            pass
        else:
            logger.debug("Pushing output record packet for anchor %s", anchor_name)

            for record_packet in self.get_grpc_record_packets(anchor_name):
                client.PushOutgoingRecordPacket(
                    OutgoingRecordPacketPush(
                        anchor_name=anchor_name,
                        record_packet=record_packet,
                    )
                )

    def get_record_packet(self, anchor_name: str) -> "RecordPacketBase":
        """
        Get a record packet.

        Parameters
        ----------
        anchor_name
            The name of the output anchor that the record packet is associated with.

        Returns
        -------
        RecordPacketBase
            The record packet associated with the anchor name.
        """
        if anchor_name not in self._record_packet_map:
            raise ValueError(f"Anchor {anchor_name} not found in repository.")

        return self._record_packet_map[anchor_name]

    def get_grpc_record_packets(self, anchor_name: str) -> List[ProtobufRecordPacket]:
        """
        Get a record packet in protobuf format.

        Parameters
        ----------
        anchor_name
            The name of the anchor to delete.

        Returns
        -------
        List[ProtobufRecordPacket]
            The list of protobuf record packets that are associated with the passed in anchor name.
        """
        record_packet = self.get_record_packet(anchor_name)

        if anchor_name not in self._record_packet_sequence:
            self._record_packet_sequence[anchor_name] = 0

        pb_packets = self._record_packet_builder.to_protobuf(
            record_packet,
            self._record_packet_sequence[anchor_name],
            self.get_anchor_progress(anchor_name),
        )

        self._record_packet_sequence[anchor_name] += len(pb_packets)
        return pb_packets

    def save_anchor_progress(self, anchor_name: str, progress: float) -> None:
        """
        Save the anchor progress.

        Parameters
        ----------
        anchor_name
            The name of the anchor to delete.
        progress
            The progress percentage of the anchor.
        """
        if not 0.0 <= progress <= 1.0:
            raise ValueError("Progress must be between 0 and 1.")

        self._anchor_progress[anchor_name] = progress

    def get_anchor_progress(self, anchor_name: str) -> float:
        """
        Get the anchor progress.

        Parameters
        ----------
        anchor_name
            The name of the anchor to delete.

        Returns
        -------
        progress
            The progress percentage of the anchor.
        """
        return self._anchor_progress.get(anchor_name, 0.0)

    def clear_repository(self) -> None:
        """Delete all data in the repository."""
        logger.debug("Clearing OutputRecordPacketRepository")
        self._record_packet_map = {}
        self._record_packet_sequence = {}
        self._anchor_progress = {}
        logger.debug(
            "Current OutputRecordPacketRepository State: %r", self._record_packet_map
        )
