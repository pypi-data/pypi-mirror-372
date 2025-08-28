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
"""Input Connection Base class definition."""
from abc import ABC, abstractmethod
from enum import IntEnum
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ayx_python_sdk.core.input_anchor_base import InputAnchorBase
    from ayx_python_sdk.core.metadata import Metadata  # noqa: F401
    from ayx_python_sdk.core.record_packet_base import RecordPacketBase


class InputConnectionStatus(IntEnum):
    """Enumeration for connection state."""

    CREATED = 1
    INITIALIZED = 2
    RECEIVING_RECORDS = 3
    CLOSED = 4


class InputConnectionBase(ABC):
    """Input connection that receives data from upstream tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Get the connection name.

        Returns
        -------
        str
            Name of the input connection.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def metadata(self) -> Optional["Metadata"]:
        """
        Get the connection metadata.

        Returns
        -------
        Metadata, optional
            The metadata associated with this input connection.

            This returns None when accessed before the input
            connection has been opened, since the metadata isn't
            known until that point.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def anchor(self) -> "InputAnchorBase":
        """
        Get the anchor this input connection is associated with.

        Returns
        -------
        InputAnchorBase
            The anchor this input connection is associated with.
        """
        raise NotImplementedError()

    @abstractmethod
    def read(self) -> "RecordPacketBase":
        """
        Read a record packet from the incoming connection.

        Returns
        -------
        RecordPacketBase
            A record packet that contains the data received by this connection.
        """
        raise NotImplementedError()

    @property
    def max_packet_size(self) -> Optional[int]:
        """
        Get the maximum number of records per packet.

        Returns
        -------
        int, optional
            The maximum number of records in a packet.
        """
        return self._get_max_packet_size()

    @max_packet_size.setter
    def max_packet_size(self, value: Optional[int]) -> None:
        """
        Set the maximum number of records per packet.

        Parameters
        ----------
        value
            The maximum number of records.
        """
        self._set_max_packet_size(value)

    @property
    @abstractmethod
    def progress(self) -> float:
        """
        Get the progress percentage of records received on this input connection.

        Returns
        -------
        float
            The progress percentage of the connection.
        """
        raise NotImplementedError()

    @progress.setter
    @abstractmethod
    def progress(self, value: float) -> None:
        """
        Set the progress percentage of records received on this input connection.

        Parameters
        ----------
        value
            The progress percentage of the connection.
        """
        raise NotImplementedError()

    def __eq__(self, other: Any) -> bool:
        """
        Compare 2 input connection instances by value.

        Parameters
        ----------
        other
            Other object to compare with this object.

        Returns
        -------
        bool
            True if all properties of this connection match the other connection.
        """
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (
            self.name == other.name
            and self.metadata == other.metadata
            and self.anchor == other.anchor
            and self.max_packet_size == other.max_packet_size
            and self.progress == other.progress
        )

    @property
    def status(self) -> InputConnectionStatus:
        """
        Get the current state of the input connection.

        Returns
        -------
        InputConnectionStatus
            Enum value corresponding to the state of the input connection
                CREATED = 1
                INITIALIZED = 2
                RECEIVING_RECORDS = 3
                CLOSED = 4
        """
        raise NotImplementedError()

    @abstractmethod
    def _get_max_packet_size(self) -> Optional[int]:
        """
        Get the max packet size allowed on this connection.

        Returns
        -------
        int, optional
            The maximum number of records in a packet.

            None if max_packet_size is not set.
        """
        raise NotImplementedError()

    @abstractmethod
    def _set_max_packet_size(self, value: Optional[int]) -> None:
        """
        Set the max packet size allowed on this connection.

        Parameters
        ----------
        value
            Max number of records allowed in each packet.
        """
        raise NotImplementedError()
