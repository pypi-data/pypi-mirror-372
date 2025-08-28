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
"""Alteryx plugin input anchor definition."""
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ayx_python_sdk.providers.e1_provider.connection_interface import (
        ConnectionInterface,
    )


class E1InputAnchorProxy:
    """Input anchor to the tool."""

    __slots__ = ["name", "allow_multiple", "optional", "connections"]

    def __init__(self, name: str, allow_multiple: bool, optional: bool):
        """Instantiate an input anchor."""
        self.name = name
        self.allow_multiple = allow_multiple
        self.optional = optional
        self.connections: List[ConnectionInterface] = []
