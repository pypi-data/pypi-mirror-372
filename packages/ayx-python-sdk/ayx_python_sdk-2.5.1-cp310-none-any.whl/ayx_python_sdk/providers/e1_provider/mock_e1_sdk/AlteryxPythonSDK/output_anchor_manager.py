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
"""Mock output anchor manager class definition."""
from typing import Mapping, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .output_anchor import OutputAnchor  # noqa


class OutputAnchorManager:
    """Output anchor manager mock."""

    def __init__(self, output_anchor_map: Mapping[str, "OutputAnchor"]):
        self._output_anchor_map = output_anchor_map

    def get_output_anchor(
        self, output_connection_name: str
    ) -> Optional["OutputAnchor"]:
        """Get an output anchor by name."""
        return self._output_anchor_map.get(output_connection_name)
