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
"""AMP Provider: Plugin Input Connection class definition."""
import logging
from typing import Optional, TYPE_CHECKING

from ayx_python_sdk.core.doc_utilities import inherit_docs
from ayx_python_sdk.core.input_connection_base import InputConnectionBase

if TYPE_CHECKING:
    from ayx_python_sdk.core import Metadata  # noqa: F401
    from ayx_python_sdk.core.input_connection_base import InputConnectionStatus
    from ayx_python_sdk.core.record_packet_base import RecordPacketBase
    from ayx_python_sdk.providers.amp_provider import AMPInputAnchor


logger = logging.getLogger(__name__)


@inherit_docs
class AMPInputConnection(InputConnectionBase):
    """Manage input connections in AMP Provider."""

    def __init__(
        self, name: str, metadata: "Metadata", anchor: "AMPInputAnchor"
    ) -> None:
        """
        Instantiate an AMP Provider input connection.

        Parameters
        ----------
        name
            Name of the input connection.
        metadata
            Metadata for the input connection.
        anchor
            Input anchor associated with the connection.
        """
        self.__name = name
        self.__metadata = metadata  # TODO: Get metadata from repository
        self.__anchor = anchor
        self.progress = 0.0

    @property
    def name(self) -> str:  # noqa: D102
        return self.__name

    @property
    def metadata(self) -> Optional["Metadata"]:  # noqa: D102
        return self.__metadata

    @property
    def anchor(self) -> "AMPInputAnchor":  # noqa: D102
        return self.__anchor

    def read(self) -> "RecordPacketBase":  # noqa: D102
        if self.metadata is None:
            raise RuntimeError("Input connection has not been opened yet.")
        logger.debug(
            "Reading record packet from input connection %s on input anchor %s",
            self.name,
            self.anchor.name,
        )
        from ayx_python_sdk.providers.amp_provider.repositories.input_record_packet_repository import (
            EmptyRecordPacketRepositoryException,
            InputRecordPacketRepository,
        )

        try:
            packet = InputRecordPacketRepository().peek_record_packet(
                self.anchor.name, self.name
            )
        except EmptyRecordPacketRepositoryException:
            raise RuntimeError("All record packets have been read from this connection")
        return packet

    def _get_max_packet_size(self) -> Optional[int]:
        from ayx_python_sdk.providers.amp_provider.repositories import (
            InputConnectionRepository,
        )

        try:
            return InputConnectionRepository().get_connection_packet_size(
                self.anchor.name, self.name
            )
        except ValueError:
            return None

    def _set_max_packet_size(self, value: Optional[int]) -> None:
        if value and value <= 0:
            raise ValueError(
                "max_packet_size must be None or an integer greater than 0."
            )

        from ayx_python_sdk.providers.amp_provider.repositories import (
            InputConnectionRepository,
        )

        InputConnectionRepository().save_connection_packet_size(
            self.anchor.name, self.name, value
        )

    @property
    def progress(self) -> float:  # noqa: D102
        return self.__progress

    @progress.setter
    def progress(self, value: float) -> None:  # noqa: D102
        if value < 0:
            raise ValueError("Progress percentage must be greater than 0.")
        self.__progress = value

    @property
    def status(self) -> "InputConnectionStatus":  # noqa: D102
        from ayx_python_sdk.providers.amp_provider.repositories import (
            InputConnectionRepository,
        )

        return InputConnectionRepository().get_connection_status(
            self.anchor.name, self.name
        )
