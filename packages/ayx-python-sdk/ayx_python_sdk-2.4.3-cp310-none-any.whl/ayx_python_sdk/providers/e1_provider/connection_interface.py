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
"""Connection class definitions."""
from enum import IntEnum
from typing import Any, List, Optional, TYPE_CHECKING

from AlteryxPythonSDK import RecordInfo, RecordRef

from ayx_python_sdk.core.observable_mixin import ObservableMixin
from ayx_python_sdk.providers.e1_provider.events import (
    ConnectionEvents,
    PluginEvents,
)
from ayx_python_sdk.providers.e1_provider.records import BaseRecordContainer

if TYPE_CHECKING:
    from ayx_python_sdk.providers.e1_provider.e1_input_anchor_proxy import (
        E1InputAnchorProxy,
    )
    from ayx_python_sdk.providers.e1_provider.e1_plugin_proxy import E1PluginProxy


ConnectionStatus = IntEnum(
    "ConnectionStatus", "CREATED INITIALIZED RECEIVING_RECORDS CLOSED"
)


class ConnectionInterface(ObservableMixin):
    """Connection interface definition."""

    __slots__ = [
        "name",
        "record_containers",
        "__record_info",
        "progress_percentage",
        "status",
        "plugin_failed",
        "anchor",
        "record_batch_size",
        "plugin_proxy",
    ]

    def __init__(
        self,
        plugin_proxy: "E1PluginProxy",
        connection_name: str,
        anchor: "E1InputAnchorProxy",
    ) -> None:
        """Instantiate a connection interface."""
        super().__init__()
        self.name = connection_name
        self.__record_info: Optional[RecordInfo] = None
        self.progress_percentage = 0.0
        self.status = ConnectionStatus.CREATED
        self.plugin_failed = False
        self.record_containers: List[BaseRecordContainer] = []
        self.anchor = anchor
        self.record_batch_size: Optional[int] = None
        self.plugin_proxy = plugin_proxy
        self.plugin_proxy.subscribe(
            PluginEvents.PLUGIN_FAILURE, self.plugin_failure_callback
        )

    @property
    def record_info(self) -> Optional[RecordInfo]:
        """Getter for record info."""
        return self.__record_info

    def add_record_container(self, container: BaseRecordContainer) -> None:
        """Add a new record container."""
        self.record_containers.append(container)

    def clear_records(self) -> None:
        """Clear all records for this connection's containers."""
        for container in self.record_containers:
            container.clear_records()

    def plugin_failure_callback(self, **_: Any) -> None:
        """Set failed status from plugin."""
        self.plugin_failed = True

    def ii_init(self, record_info: RecordInfo) -> bool:
        """Initialize the connection."""
        # DO NOT REMOVE NEXT LINE: The base SDK has issues with sys.path updates,
        # and in order to fix some dependency resolution issues we have to update it again here
        self.plugin_proxy.update_sys_path()
        self.status = ConnectionStatus.INITIALIZED
        self.__record_info = record_info
        self.notify_topic(ConnectionEvents.CONNECTION_INITIALIZED, connection=self)

        return not self.plugin_failed

    def ii_push_record(self, record: RecordRef) -> bool:
        """Receive a record."""
        self.status = ConnectionStatus.RECEIVING_RECORDS

        for container in self.record_containers:
            container.add_record(record)

        self.notify_topic(ConnectionEvents.RECORD_RECEIVED, connection=self)

        return not self.plugin_failed

    def ii_update_progress(self, d_percent: float) -> None:
        """Update progress of incoming data."""
        self.progress_percentage = max(d_percent, 0)
        self.notify_topic(
            ConnectionEvents.PROGRESS_UPDATE, connection=self, percent=d_percent
        )

    def ii_close(self) -> None:
        """Close the connection."""
        self.status = ConnectionStatus.CLOSED
        self.notify_topic(ConnectionEvents.CONNECTION_CLOSED, connection=self)
