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
"""AMP Provider: Plugin Output Anchor class definition."""
import logging
from typing import Optional, TYPE_CHECKING

from ayx_python_sdk.core import (
    Metadata,
    OutputAnchorBase,
    RecordPacketBase,
)
from ayx_python_sdk.core.doc_utilities import inherit_docs
from ayx_python_sdk.providers.amp_provider.repositories import (
    OutputMetadataRepository,
    OutputRecordPacketRepository,
)

if TYPE_CHECKING:
    import pandas as pd  # noqa: F401

logger = logging.getLogger(__name__)


@inherit_docs
class AMPOutputAnchor(OutputAnchorBase):
    """Manage the tool's output anchor in AMP Provider."""

    def __init__(
        self,
        name: str,
        allow_multiple: bool = False,
        optional: bool = False,
        num_connections: int = 0,
    ) -> None:
        self.__name: str = name
        self.__allow_multiple: bool = allow_multiple
        self.__optional: bool = optional
        self.__num_connections: int = num_connections
        self.written_dataframe: Optional["pd.Dataframe"] = None
        logger.debug("Created output anchor %s", self.name)

    @property
    def name(self) -> str:  # noqa: D102
        return self.__name

    @property
    def allow_multiple(self) -> bool:  # noqa: D102
        return self.__allow_multiple

    @property
    def optional(self) -> bool:  # noqa: D102
        return self.__optional

    @property
    def num_connections(self) -> int:  # noqa: D102
        return self.__num_connections

    @property
    def is_open(self) -> bool:  # noqa: D102
        try:
            OutputMetadataRepository().get_metadata(self.name)
        except ValueError:
            return False
        else:
            return True

    @property
    def metadata(self) -> Optional["Metadata"]:  # noqa: D102
        if self.is_open:
            return OutputMetadataRepository().get_metadata(self.name)
        return None

    def open(self, metadata: "Metadata") -> None:  # noqa: D102
        logger.debug("Opening Output Anchor %s", self.name)
        OutputMetadataRepository().save_metadata(self.name, metadata)

    def write(self, record_packet: "RecordPacketBase") -> None:  # noqa: D102
        if self.metadata is None:
            raise RuntimeError("Output anchor is not open.")

        if record_packet.metadata != self.metadata:
            raise RuntimeError(
                "Output anchor's metadata does not match incoming record packet."
            )

        OutputRecordPacketRepository().save_record_packet(self.name, record_packet)

    def flush(self) -> None:  # noqa: D102
        raise NotImplementedError

    def close(self) -> None:  # noqa: D102
        logger.debug("Closing Output Anchor %s", self.name)
        OutputMetadataRepository().delete_metadata(self.name)

    def update_progress(self, percentage: float) -> None:  # noqa: D102
        OutputRecordPacketRepository().save_anchor_progress(self.name, percentage)
