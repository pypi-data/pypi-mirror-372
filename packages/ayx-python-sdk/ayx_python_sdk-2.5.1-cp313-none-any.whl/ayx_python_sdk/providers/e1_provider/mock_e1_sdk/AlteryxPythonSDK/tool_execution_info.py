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
"""Class definition for tool execution information."""
from typing import List, Optional


class ToolExecutionInfo:
    """Tool execution info class."""

    def __init__(self) -> None:
        """Construct a tool execution information object."""
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.infos: List[str] = []
        self.output_workflow_xml: Optional[str] = None
        self.progress: float = 0.0

    def add_error(self, error: str) -> None:
        """Add an error message to the info."""
        self.errors.append(error)

    def add_warning(self, warning: str) -> None:
        """Add an warning message to the info."""
        self.warnings.append(warning)

    def add_info(self, info: str) -> None:
        """Add an info message to the info."""
        self.infos.append(info)

    def set_output_workflow_xml(self, xml: str) -> None:
        """Track the output tool workflow XML."""
        self.output_workflow_xml = xml
