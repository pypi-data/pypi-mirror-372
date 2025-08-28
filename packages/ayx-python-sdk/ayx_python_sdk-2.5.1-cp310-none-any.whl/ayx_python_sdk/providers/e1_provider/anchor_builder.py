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
"""Alteryx tool configuration definition."""
from typing import Any, Dict, List

from AlteryxPythonSDK import OutputAnchorManager

from ayx_python_sdk.providers.e1_provider.e1_input_anchor_proxy import (
    E1InputAnchorProxy,
)
from ayx_python_sdk.providers.e1_provider.e1_output_anchor_proxy import (
    E1OutputAnchorProxy,
)


class AnchorBuilder:
    """Anchor builder definition."""

    __slots__ = ["tool_config", "output_anchor_mgr"]

    def __init__(
        self, tool_config: Dict[str, Any], output_anchor_mgr: OutputAnchorManager
    ):
        """Initialize a tool configuration."""
        self.tool_config = tool_config
        self.output_anchor_mgr = output_anchor_mgr

    def build_input_anchors(self) -> List[E1InputAnchorProxy]:
        """Build the input anchors based on tool config settings."""
        anchor_settings = self.tool_config["AlteryxJavaScriptPlugin"]["GuiSettings"]

        input_anchors = anchor_settings.get("InputConnections")
        if not isinstance(input_anchors, dict):
            input_anchor_configs: List[Dict] = []
        else:
            input_anchor_configs_raw = input_anchors.get("Connection")
            if not isinstance(input_anchor_configs_raw, dict) and not isinstance(
                input_anchor_configs_raw, list
            ):
                input_anchor_configs = []
            else:
                if not isinstance(input_anchor_configs_raw, list):
                    input_anchor_configs = [input_anchor_configs_raw]
                else:
                    input_anchor_configs = input_anchor_configs_raw

        return [
            E1InputAnchorProxy(
                config["@Name"],
                config.get("@AllowMultiple", "false").lower() == "true",
                config["@Optional"].lower() == "true",
            )
            for config in input_anchor_configs
        ]

    def build_output_anchors(self) -> List[E1OutputAnchorProxy]:
        """Build the output anchors based on tool config settings."""
        anchor_settings = self.tool_config["AlteryxJavaScriptPlugin"]["GuiSettings"]

        output_anchors = anchor_settings.get("OutputConnections")

        if not isinstance(output_anchors, dict):
            output_anchor_configs: List[Dict] = []
        else:
            output_anchor_configs_raw = output_anchors.get("Connection")
            if not isinstance(output_anchor_configs_raw, dict) and not isinstance(
                output_anchor_configs_raw, list
            ):
                output_anchor_configs = []
            else:
                if not isinstance(output_anchor_configs_raw, list):
                    output_anchor_configs = [output_anchor_configs_raw]
                else:
                    output_anchor_configs = output_anchor_configs_raw

        return [
            E1OutputAnchorProxy(
                config["@Name"],
                config.get("@AllowMultiple", "true").lower() == "true",
                config["@Optional"].lower() == "true",
                self.output_anchor_mgr,
            )
            for config in output_anchor_configs
        ]
