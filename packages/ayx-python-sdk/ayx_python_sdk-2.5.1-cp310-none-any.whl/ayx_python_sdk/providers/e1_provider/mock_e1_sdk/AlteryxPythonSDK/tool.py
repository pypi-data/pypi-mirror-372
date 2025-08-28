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
"""Tool definition."""
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .alteryx_engine import AlteryxEngine


class Tool:
    """Instance of a tool in a workflow along with associated data structures."""

    def __init__(self, engine: "AlteryxEngine", plugin_instance: Any) -> None:
        """Construct a new tool object."""
        self.engine = engine
        self.plugin_instance = plugin_instance
        self.output_manager = None
        self.tool_id = None
