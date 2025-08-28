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
"""Output Anchor Description implementation."""
from abc import ABC, abstractmethod
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ayx_python_sdk.core.metadata import Metadata
    from ayx_python_sdk.core.record_packet_base import RecordPacketBase


class OutputAnchorBase(ABC):
    """Output Anchor Base class definition."""

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Get the name of the output anchor.

        Returns
        -------
        str
            The name of the output anchor.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def allow_multiple(self) -> bool:
        """
        Get the status that indicates if multiple connections are allowed.

        Returns
        -------
        bool
            Boolean value that indicates if multiple connections are allowed.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def optional(self) -> bool:
        """
        Get the status that indicates if the output anchor is optional.

        Returns
        -------
        bool
            Boolean value that indicates if output anchor is optional.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def num_connections(self) -> int:
        """
        Get the number of connections attached to the anchor.

        Returns
        -------
        int
            The number of downstream connections on this anchor.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def is_open(self) -> bool:
        """Get the status that indicates if the anchor is open."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def metadata(self) -> Optional["Metadata"]:
        """Get the metadata for the anchor."""
        raise NotImplementedError()

    @abstractmethod
    def open(self, metadata: "Metadata") -> None:
        """
        Open the output anchor.

        Write the outgoing record metadata and open this connection for
        outgoing packets.

        Parameters
        ----------
        metadata
            The metadata to set for this anchor.
        """
        raise NotImplementedError()

    @abstractmethod
    def write(self, record_packet: "RecordPacketBase") -> None:
        """
        Write a RecordPacket to the outgoing connection.

        Parameters
        ----------
        record_packet
            The record packet to write to the output anchor.
        """
        raise NotImplementedError()

    @abstractmethod
    def flush(self) -> None:
        """Flush the written records for this output connection."""
        raise NotImplementedError()

    @abstractmethod
    def close(self) -> None:
        """Close the outgoing connection."""
        raise NotImplementedError()

    @abstractmethod
    def update_progress(self, percentage: float) -> None:
        """
        Update the progress on downstream connections.

        Parameters
        ----------
        percentage
            The percentage to write to Designer, that indicates the progress of
            output on this anchor.
        """
        raise NotImplementedError()

    def __eq__(self, other: Any) -> bool:
        """Compare 2 output anchor instances by value."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (
            self.name == other.name
            and self.allow_multiple == other.allow_multiple
            and self.is_open == other.is_open
            and self.optional == other.optional
            and self.metadata == other.metadata
            and self.num_connections == other.num_connections
        )
