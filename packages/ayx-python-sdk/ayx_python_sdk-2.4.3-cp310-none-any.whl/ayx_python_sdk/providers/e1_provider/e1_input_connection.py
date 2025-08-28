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
"""E1 SDK Input Connection class."""
from typing import Optional, TYPE_CHECKING

from ayx_python_sdk.core.doc_utilities import inherit_docs
from ayx_python_sdk.core.input_connection_base import InputConnectionBase
from ayx_python_sdk.providers.e1_provider.connection_interface import (
    ConnectionInterface,
)
from ayx_python_sdk.providers.e1_provider.e1_record_packet import E1RecordPacket
from ayx_python_sdk.providers.e1_provider.utilities import (
    convert_record_info_to_metadata,
)

if TYPE_CHECKING:
    from ayx_python_sdk.core.metadata import Metadata  # noqa: F401
    from ayx_python_sdk.core.record_packet import RecordPacket
    from ayx_python_sdk.providers.e1_provider.e1_input_anchor import E1InputAnchor


@inherit_docs
class E1InputConnection(InputConnectionBase):
    """Class for managing Inputs in E1 SDK."""

    def __init__(self, conn_interface: "ConnectionInterface") -> None:
        """Instantiate the input connection."""
        self._conn_interface = conn_interface

    @property
    def name(self) -> str:  # noqa: D102
        return self._conn_interface.name

    @property
    def metadata(self) -> Optional["Metadata"]:  # noqa: D102
        if self._conn_interface.record_info is None:
            return None

        return convert_record_info_to_metadata(self._conn_interface.record_info)

    @property
    def anchor(self) -> "E1InputAnchor":  # noqa: D102
        from ayx_python_sdk.providers.e1_provider import E1InputAnchor

        return E1InputAnchor(self._conn_interface.anchor)

    def read(self) -> "RecordPacket":  # noqa: D102
        if self.metadata is None:
            raise RuntimeError("Input connection has not been opened yet.")

        record_dataframe = self._conn_interface.record_containers[0].build_dataframe()

        packet = E1RecordPacket.from_dataframe(self.metadata, record_dataframe)
        self._conn_interface.clear_records()
        return packet

    def _get_max_packet_size(self) -> Optional[int]:
        return self._conn_interface.record_batch_size

    def _set_max_packet_size(self, value: Optional[int]) -> None:
        if value and value <= 0:
            raise ValueError(
                "max_packet_size must be None or an integer greater than 0."
            )

        self._conn_interface.record_batch_size = value

    @property
    def progress(self) -> float:  # noqa: D102
        return self._conn_interface.progress_percentage

    @progress.setter
    def progress(self, value: float) -> None:  # noqa: D102
        if value < 0:
            raise ValueError("Progress percentage must be greater than 0.")
        self._conn_interface.progress_percentage = value
