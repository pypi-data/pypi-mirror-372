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
"""E1 SDK Driver Class."""
from typing import Optional, TYPE_CHECKING, Type

from ayx_python_sdk.providers.e1_provider.e1_input_connection import E1InputConnection
from ayx_python_sdk.providers.e1_provider.records import ParsedRecordContainer

if TYPE_CHECKING:
    from ayx_python_sdk.core.plugin import Plugin  # noqa: F401
    from ayx_python_sdk.core.provider_base import ProviderBase
    from ayx_python_sdk.providers.e1_provider.connection_interface import (
        ConnectionInterface,
    )


class E1PluginDriver:
    """Wrapper around the plugin to expose only interfaces defined for a provider."""

    def __init__(self, user_plugin_class: Type["Plugin"], provider: "ProviderBase"):
        """Construct the E1Provider."""
        self._provider = provider
        self._user_plugin_class = user_plugin_class
        self._user_plugin: Optional["Plugin"] = None

    def initialize_plugin(self) -> None:
        """Initialize plugin."""
        self._user_plugin = self._user_plugin_class(self._provider)

    def initialize_connection(self, connection: "ConnectionInterface") -> None:
        """Initialize a connection."""
        if connection.record_info is None:
            raise RuntimeError("Record info must be present before setting containers.")

        if self._user_plugin is None:
            raise ValueError("user_plugin hasn't been set.")

        connection.add_record_container(ParsedRecordContainer(connection.record_info))
        self._user_plugin.on_input_connection_opened(E1InputConnection(connection))

    def on_record_packet(self, connection: "ConnectionInterface") -> None:
        """Handle the record packet received through the input connection."""
        if self._user_plugin is None:
            raise ValueError("user_plugin hasn't been set.")

        self._user_plugin.on_record_packet(E1InputConnection(connection))

    def on_complete(self) -> None:
        """Close plugin code after all records have finished streaming."""
        if self._user_plugin is None:
            raise ValueError("user_plugin hasn't been set.")
        self._user_plugin.on_complete()
