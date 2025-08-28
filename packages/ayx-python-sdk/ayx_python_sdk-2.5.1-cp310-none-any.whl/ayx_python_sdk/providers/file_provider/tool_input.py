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
"""Alteryx Designer environment information."""
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, validator


class ToolDefinition(BaseModel):
    """
    ToolDefinition validates the tool information for the tool input.

    Parameters
    ----------
    plugin
        The class name of the plugin being run.
    path
        The path to the plugin being run.
    """

    plugin: str
    path: Path


class AnchorDefinition(BaseModel):
    """
    AnchorDefinition validates the anchor information for the tool input.

    Parameters
    ----------
    anchor_name
        The name of the anchor that the records and metadata are assoiciated with.
    records
        The anchor record data.
    metadata
        The anchor metadata information.
    """

    anchor_name: str
    records: Path
    metadata: Path


class ToolInput(BaseModel):
    """
    ToolInput validates the input JSON for the user input to the file provider.

    Parameters
    ----------
    tool
        A ToolDefinition object with 2 inputs, path and plugin, that contain the path
        to the plugin and the plugin name respectively.
    tool_config
        The path to the tool configuration file.
    workflow_config
        The path to the workflow configuration file.
    inputs
        A list of AnchorDefinition objects with 3 inputs, anchor_name, records, and metadata,
        that specify the anchor the input information corresponds to, the record information for that anchor,
        and the metadata information for that anchor respectively.
     outputs
        A list of AnchorDefinition objects with 3 inputs, anchor_name, records, and metadata, that specify the anchor
        the output information corresponds to, the file where the record information for that anchor will
        be stored, and the file where the metadata information for that anchor will be stored respectively.
    update_tool_config
        An optional path that indicates whether to update the tool's config. If it is set,
        the config will be updated at the specified path.
    """

    tool: ToolDefinition
    tool_config: Path
    workflow_config: Path
    inputs: Optional[List[AnchorDefinition]]
    outputs: Optional[List[AnchorDefinition]]
    update_tool_config: Optional[Path]

    @validator("inputs", "outputs", always=True, pre=True)
    def anchor_is_none(cls, v):  # type: ignore  # noqa: N805
        """
        Set the inputs and outputs equal to an empty list if they aren't specified.

        Parameters
        ----------
        v
            The inputs or the outputs optional list of dictionaries.

        Returns
        -------
        List[Dict[str, str]]
            An empty list or the inputs or outputs.
        """
        return v or []
