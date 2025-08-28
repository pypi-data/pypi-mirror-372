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
"""File Provider Input Connection class."""
from typing import Optional, TYPE_CHECKING

from ayx_python_sdk.core.doc_utilities import inherit_docs
from ayx_python_sdk.core.input_connection_base import InputConnectionBase
from ayx_python_sdk.core.metadata import Metadata
from ayx_python_sdk.core.record_packet import RecordPacket

import pandas as pd


if TYPE_CHECKING:
    from ayx_python_sdk.providers.file_provider.file_provider_input_anchor import (
        FileProviderInputAnchor,
    )


@inherit_docs
class FileProviderInputConnection(InputConnectionBase):
    """An input connection contains incoming record and metadata information."""

    def __init__(
        self,
        name: str,
        metadata: Metadata,
        packet: Optional[RecordPacket] = None,
        anchor: Optional["FileProviderInputAnchor"] = None,
    ) -> None:
        """
        Instantiate a file provider input connection.

        Parameters
        ----------
        name
            Name of the input connection.
        metadata
            Metadata for the input connections.
        packet
            Record information for the input connection.
        anchor
            Input anchor associated with this connection.
        """
        if packet and packet.metadata != metadata:
            raise ValueError(
                "Record packet metadata must be the same as anchor metadata."
            )

        self.__packet = packet
        self.__name = name
        self.__metadata = metadata
        self.__anchor = anchor
        self.max_packet_size = None
        self.progress = 0

    @property
    def name(self) -> str:  # noqa: D102
        return self.__name

    @property
    def metadata(self) -> Optional[Metadata]:  # noqa: D102
        return self.__metadata

    @property
    def anchor(self) -> "FileProviderInputAnchor":  # noqa: D102
        if self.__anchor:
            return self.__anchor

        raise RuntimeError("This input connection is not associated with an anchor.")

    def read(self) -> RecordPacket:  # noqa: D102
        if self.metadata is None:
            raise ValueError("Metadata must be set.")

        return self.__packet or RecordPacket(
            self.metadata, pd.DataFrame(columns=[field.name for field in self.metadata])
        )

    def _get_max_packet_size(self) -> Optional[int]:
        return self.__max_packet_size

    def _set_max_packet_size(self, value: Optional[int]) -> None:
        """
        File provider doesn't use max_packet size - automatically set to None.

        Otherwise, a user could try and set max packet size for the file provider and would not know why it was not affecting their tool.
        """
        if value is not None:
            return  # TODO: warn user that the file provider does not currently support setting max_packet_size
        self.__max_packet_size = value

    @property
    def progress(self) -> float:  # noqa: D102
        return self.__progress

    @progress.setter
    def progress(self, value: float) -> None:  # noqa: D102
        if value < 0:
            raise ValueError("Progress percentage must be greater than 0.")
        self.__progress = value
