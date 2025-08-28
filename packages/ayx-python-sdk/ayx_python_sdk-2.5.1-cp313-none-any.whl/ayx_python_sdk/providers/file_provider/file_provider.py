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
"""File provider for testing a tool outside of Designer."""
from logging import Logger
from pathlib import Path
from typing import Dict, List, Optional, TYPE_CHECKING, Type

from ayx_python_sdk.core.doc_utilities import inherit_docs
from ayx_python_sdk.core.plugin import Plugin
from ayx_python_sdk.core.provider_base import ProviderBase
from ayx_python_sdk.core.record_packet import RecordPacket
from ayx_python_sdk.providers.file_provider.environment import Environment
from ayx_python_sdk.providers.file_provider.file_adapter import FileAdapter
from ayx_python_sdk.providers.file_provider.file_provider_dcm import FileProviderDCM
from ayx_python_sdk.providers.file_provider.file_provider_input_connection import (
    FileProviderInputConnection,
)
from ayx_python_sdk.providers.file_provider.iox import IO

import deprecation

if TYPE_CHECKING:
    from ayx_python_sdk.providers.file_provider.file_provider_input_anchor import (
        FileProviderInputAnchor,
    )
    from ayx_python_sdk.providers.file_provider.file_provider_output_anchor import (
        FileProviderOutputAnchor,
    )
    from ayx_python_sdk.providers.file_provider.tool_input import AnchorDefinition


user_plugin_class: Optional[Type[Plugin]] = None


@deprecation.deprecated(
    deprecated_in="1.0.3",
    removed_in="2.0.0",
    details="Use the Plugin CLI's test harness instead.",
)
@inherit_docs
class FileProvider(ProviderBase):
    """
    File provider implementation.

    The file provider will instantiate input and output connections for the
    tool from input files and pass information along to the tool plugin.
    """

    def __init__(
        self,
        tool_config: Path,
        workflow_config: Path,
        inputs: "List[AnchorDefinition]",
        outputs: "List[AnchorDefinition]",
        update_tool_config: Optional[Path],
    ):
        """
        Instantiate the file provider.

        Parameters
        ----------
        tool_config
            Tool configuration file.
        workflow_config
            Configuration file for anchor information.
        inputs
            The incoming input information.
        outputs
            The information that says where to store the outgoing information.
        update_tool_config
            An optional path that indicates whether to update the tool's config. If it is set,
            the config will be updated at the specified path.
        """
        super().__init__()
        self.__logger = Logger("File Provider")
        self.__io = IO()
        self.__dcm = FileProviderDCM()
        self.__environment = Environment(update_tool_config)

        self.adapter = FileAdapter(tool_config, workflow_config)
        self.input_anchors = self.adapter.build_input_anchors()
        self.output_anchors = self.adapter.build_output_anchors()

        for input in inputs:
            name = input.anchor_name
            metadata_file = Path(input.metadata)
            csv_file = Path(input.records)
            self.__add_input_connection_to_anchor(name, metadata_file, csv_file)
        # Add file information to the output anchors
        for output in outputs:
            name = output.anchor_name
            metadata_file = Path(output.metadata)
            csv_file = Path(output.records)
            self.__populate_output_anchor(name, metadata_file, csv_file)

    @property
    def tool_config(self) -> Dict:  # noqa: D102
        return self.adapter.tool_config

    @property
    def io(self) -> IO:  # noqa: D102
        return self.__io

    @property
    def dcm(self) -> FileProviderDCM:  # noqa: D102
        return self.__dcm

    @property
    def environment(self) -> Environment:  # noqa: D102
        return self.__environment

    @property
    def logger(self) -> "Logger":  # noqa: D102
        return self.__logger

    def __add_input_connection_to_anchor(
        self, name: str, metadata_file: Path, csv_file: Path
    ) -> None:
        """
        Build an input connection from the provided metadata and record files.

        Parameters
        ----------
        name
            The input anchor the connection is associated with.
        metadata_file
            The input metadata associated with this connection.
        csv_file
            The input record info associated with this connection.
        """
        metadata = self.adapter.xml_to_metadata(metadata_file)
        dataframe = self.adapter.csv_to_dataframe(csv_file)
        # TODO deal with max_packet_size
        record_packet = RecordPacket.from_dataframe(metadata, dataframe)
        input_anchor = self.get_input_anchor(name)
        # TODO figure out better input connection name
        input_connection = FileProviderInputConnection(
            self.adapter.name, metadata, record_packet, input_anchor
        )
        input_anchor.connections.append(input_connection)

    def __populate_output_anchor(
        self, name: str, metadata_file: Path, csv_file: Path
    ) -> None:
        """
        Add the required file information to the output anchor.

        Parameters
        ----------
        name
            The output anchor the file information should be added to.
        metadata_file
            The output metadata file associated with this anchor.
        csv_file
            The output record info file associated with this connection.
        """
        output_anchor = self.get_output_anchor(name)
        output_anchor.metadata_file = metadata_file
        output_anchor.record_file = csv_file
        output_anchor.file_adapter = self.adapter

    def get_input_anchor(self, name: str) -> "FileProviderInputAnchor":  # noqa: D102
        for input_anchor in self.input_anchors:
            if name == input_anchor.name:
                return input_anchor

        raise RuntimeError("There was no input anchor found with name {}".format(name))

    def get_output_anchor(self, name: str) -> "FileProviderOutputAnchor":  # noqa: D102
        for output_anchor in self.output_anchors:
            if name == output_anchor.name:
                return output_anchor

        raise RuntimeError("There was no output anchor found with name {}".format(name))
