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
"""Class that saves tool configuration information."""
import copy
from typing import Any, Dict

from ayx_python_sdk.providers.amp_provider.builders.tool_config_builder import (
    ToolConfigBuilder,
)
from ayx_python_sdk.providers.amp_provider.repositories.grpc_repository import (
    GrpcRepository,
)
from ayx_python_sdk.providers.amp_provider.repositories.singleton import Singleton
from ayx_python_sdk.providers.amp_provider.resources.generated.output_message_data_pb2 import (
    OutputMessageData,
    OutputMessageTypes,
)


class ToolConfigRepository(metaclass=Singleton):
    """Repository that stores tool configuration information."""

    _tool_config_builder = ToolConfigBuilder()

    def __init__(self) -> None:
        """Initialize the tool configuration repository."""
        self._tool_config: Dict[str, Any] = {}

    def save_tool_config(self, tool_config: Dict[str, Any]) -> None:
        """
        Save tool configuration dictionary.

        Parameters
        ----------
        tool_config
            Dictionary form of the Tool Config XML.
        """
        if tool_config != self._tool_config:
            self._tool_config = tool_config

            try:
                client = GrpcRepository().get_sdk_engine_client()
            except ValueError:
                # Don't save if client isn't ready
                pass
            else:
                client.OutputMessage(
                    OutputMessageData(
                        message_type=OutputMessageTypes.OMT_UpdateOutputConfigXml,
                        message=self._tool_config_builder.to_xml(tool_config),
                    )
                )

    def save_xml_tool_config(self, tool_config_xml: str) -> None:
        """
        Save the tool configuration xml as a dictionary.

        Parameters
        ----------
        tool_config_xml
            The Tool Config XML as a raw string.
        """
        self.save_tool_config(self._tool_config_builder.from_xml(tool_config_xml))

    def get_tool_config(self) -> Dict[str, Any]:
        """
        Get the tool configuration.

        Returns
        -------
        Dict[str, Any]
            The Tool Config XML associated with the current plugin.
        """
        return copy.deepcopy(self._tool_config)

    def clear_repository(self) -> None:
        """Delete all data in the repository."""
        self._tool_config = {}
