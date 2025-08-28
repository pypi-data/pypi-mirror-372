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
"""AMP Provider: SDK Provider class definition."""

# from AyxPythonSdk.ayx_python_sdk.providers.amp_provider.amp_environment import AMPEnvironment
import logging
from collections import defaultdict
from typing import Any, Dict, TYPE_CHECKING

from ayx_python_sdk.providers.amp_provider.amp_environment_v2 import AMPEnvironmentV2
from ayx_python_sdk.providers.amp_provider.amp_io_components import (
    ControlIOBuffer,
    StreamIOBuffer,
)
from ayx_python_sdk.providers.amp_provider.grpc_helpers.control_msgs import (
    new_ctrl_out_metadata_msg,
    new_ctrl_out_save_config,
)

import xmltodict

if TYPE_CHECKING:
    from ayx_python_sdk.providers.amp_provider.resources.generated.sdk_tool_service_v2_pb2 import (
        ControlIn,
    )

    from pyarrow import Schema

# Update for docs needed since we're not inheriting from legacy ProviderBase now.


class AMPProviderV2:
    """Class that provides resources to plugins that are run with the AMP Provider."""

    def __init__(self) -> None:
        """Initialize the AMP resource provider."""
        self.__environment: AMPEnvironmentV2 = AMPEnvironmentV2()
        self.__ctrl_io: "ControlIOBuffer" = ControlIOBuffer()
        self.__record_transfer_io: StreamIOBuffer = StreamIOBuffer()
        self.incoming_anchors: defaultdict = defaultdict(dict)
        self.outgoing_anchors: dict = {}
        self.logger = logging.getLogger()

    @property
    def io(self) -> "ControlIOBuffer":  # noqa: D102
        return self.__ctrl_io

    @property
    def environment(self) -> "AMPEnvironmentV2":  # noqa: D102
        return self.__environment

    @property
    def record_io(self) -> "StreamIOBuffer":  # noqa: D102
        return self.__record_transfer_io

    @property
    def dcm(self) -> "ControlIOBuffer":  # noqa: D102
        return self.__ctrl_io

    @property
    def tool_config(self) -> Dict:
        """
        Get the tool config from the tool's config UI in Designer.

        Returns
        -------
        Dict[str, Any]
            The Tool Config associated with the current plugin, in the form of a Python dictionary.
        """
        return self.environment.tool_config

    def save_tool_config(self, tool_config: Dict[str, Any]) -> None:  # noqa: D102
        """
        Encode the tool configuration as a Python dictionary and send it to Designer.

        Parameters
        ----------
        tool_config
            Dictionary form of the Tool Config XML.
        """
        unparsed: str = xmltodict.unparse(
            {"Configuration": tool_config}, short_empty_elements=True
        )
        msg = new_ctrl_out_save_config(unparsed)
        try:
            self.__ctrl_io.push_ctrl_out(msg)
            self.__environment.update_tool_config(tool_config)
            self.logger.debug(self.__environment.tool_config)
        except Exception as e:
            self.__ctrl_io.warn("Failed to update tool config.")
            self.logger.warn("tool_config save exception was: %s", repr(e))

    def push_outgoing_metadata(
        self, anchor_name: str, metadata: "Schema"
    ) -> None:  # noqa: D102
        metadata_msg = new_ctrl_out_metadata_msg(anchor_name, metadata)
        self.__ctrl_io.push_ctrl_out(metadata_msg)

    def write_to_anchor(self, name: str, data: object) -> None:  # noqa: D102
        self.__record_transfer_io.write_to_buffer(name, data)

    def close_outgoing_anchor(self, name: str) -> None:  # noqa: D102
        self.__record_transfer_io.push_close_anchor_msg(name)

    def set_anchors(self, init_request: "ControlIn") -> None:  # noqa: D102
        for anchor in init_request.plugin_initialization_data.incomingAnchors:
            for conn in anchor.connections:
                self.incoming_anchors[anchor.name][conn.name] = {
                    "name": conn.name,
                    "metadata": conn.metadata,
                }
        for anchor in init_request.plugin_initialization_data.outgoingAnchors:
            self.outgoing_anchors[anchor.name] = {
                "name": anchor.name,
                "metadata": anchor.metadata,
                "num_connections": anchor.num_connections,
            }
