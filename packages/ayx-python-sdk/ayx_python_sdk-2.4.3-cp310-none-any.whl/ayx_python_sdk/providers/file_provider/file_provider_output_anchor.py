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
"""File provider output anchor class."""
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from ayx_python_sdk.core import OutputAnchorBase
from ayx_python_sdk.core.doc_utilities import inherit_docs

if TYPE_CHECKING:
    from ayx_python_sdk.core.metadata import Metadata
    from ayx_python_sdk.core.record_packet import RecordPacketBase
    from ayx_python_sdk.providers.file_provider.file_adapter import (  # noqa: F401
        FileAdapter,
    )  # noqa: F401


@inherit_docs
class FileProviderOutputAnchor(OutputAnchorBase):
    """The output anchor contains outgoing record and metadata information."""

    def __init__(
        self, name: str, allow_multiple: bool = False, optional: bool = False
    ) -> None:
        """
        Instantiate a file provider output anchor.

        Parameters
        ----------
        name
            Name of the output anchor.
        allow_multiple
            Indicates whether to allow more than one connection.
        optional
            Indicates whether the anchor is optional or not.
        """
        self.__name = name
        self.__allow_multiple = allow_multiple
        self.__optional = optional
        self.__metadata: Optional["Metadata"] = None
        self.__is_closed: bool = True
        self.__num_connections: int = 0
        # TODO the file paths and FileAdapter should be populated by the constructor
        self.metadata_file: Path = Path()
        self.record_file: Path = Path()
        self.file_adapter: Optional["FileAdapter"] = None

    def update_progress(self, percentage: float) -> None:
        """File provider does not need to update progress, so pass."""

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
        return not self.__is_closed

    @property
    def metadata(self) -> Optional["Metadata"]:  # noqa: D102
        return self.__metadata

    def open(self, metadata: "Metadata") -> None:  # noqa: D102
        if not self.file_adapter:
            raise RuntimeError("File adapter must be set to open the output anchor.")

        self.__metadata = metadata
        # TODO we should just have a helper function here
        self.file_adapter.metadata_to_xml(self.metadata_file, self.__metadata)
        self.__is_closed = False

    def write(self, record_packet: "RecordPacketBase") -> None:  # noqa: D102
        if not self.__metadata or not self.file_adapter:
            raise RuntimeError(
                "Output anchor must be opened before it can be written to."
            )

        if self.__metadata != record_packet.metadata:
            raise RuntimeError(
                "Output anchor's metadata must match the incoming record packet's metadata."
            )

        dataframe = record_packet.to_dataframe()
        # TODO This will overwrite the entire CSV file. It should have the option to append the records to one that already exists.
        self.file_adapter.dataframe_to_csv(self.record_file, dataframe)

    def flush(self) -> None:
        """File provider does not need to flush records, so pass."""

    def close(self) -> None:  # noqa: D102
        self.__is_closed = True
