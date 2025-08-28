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
from typing import List

from ayx_python_sdk.core.doc_utilities import inherit_docs
from ayx_python_sdk.core.input_anchor_base import InputAnchorBase
from ayx_python_sdk.core.input_connection_base import InputConnectionBase
from ayx_python_sdk.providers.e1_provider.e1_input_anchor_proxy import (
    E1InputAnchorProxy,
)
from ayx_python_sdk.providers.e1_provider.e1_input_connection import E1InputConnection


@inherit_docs
class E1InputAnchor(InputAnchorBase):
    """Input anchor to the tool."""

    def __init__(self, input_anchor_proxy: E1InputAnchorProxy) -> None:
        """Instantiate an input anchor."""
        self._input_anchor_proxy = input_anchor_proxy

    @property
    def name(self) -> str:  # noqa: D102
        return self._input_anchor_proxy.name

    @property
    def allow_multiple(self) -> bool:  # noqa: D102
        return self._input_anchor_proxy.allow_multiple

    @property
    def optional(self) -> bool:  # noqa: D102
        return self._input_anchor_proxy.optional

    @property
    def connections(self) -> List[InputConnectionBase]:  # noqa: D102
        return [
            E1InputConnection(connection)
            for connection in self._input_anchor_proxy.connections
        ]
