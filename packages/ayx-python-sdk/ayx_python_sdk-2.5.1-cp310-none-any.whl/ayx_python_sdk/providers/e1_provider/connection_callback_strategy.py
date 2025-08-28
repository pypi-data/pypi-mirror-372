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
"""Connection callback strategy definitions."""
from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

from .connection_interface import ConnectionInterface

if TYPE_CHECKING:
    from ayx_python_sdk.providers.e1_provider.e1_plugin_proxy import E1PluginProxy


class ConnectionCallbackStrategy(ABC):
    """ABC for callback strategy."""

    __slots__ = ["plugin_proxy"]

    def __init__(self, plugin_proxy: "E1PluginProxy") -> None:
        """Construct a callback strategy."""
        self.plugin_proxy = plugin_proxy

    def update_progress_callback(self, **_: Any) -> None:
        """Update input progress percentage."""
        import numpy as np

        percent = float(
            np.mean(
                [
                    connection.progress_percentage
                    for anchor in self.plugin_proxy.input_anchors
                    for connection in anchor.connections
                ]
            )
        )

        self.plugin_proxy.io.update_progress(percent)

        for anchor in self.plugin_proxy.output_anchors:
            anchor.update_progress(percent)

    def connection_initialized_callback(
        self, connection: ConnectionInterface, **_: Any
    ) -> None:
        """Run callback for connection initialization."""
        try:
            if not self.plugin_proxy.all_required_connections_connected:
                self.plugin_proxy.raise_missing_inputs()

            if (
                not self.plugin_proxy.initialized
                and not self.plugin_proxy.failure_occurred
            ):
                if self.plugin_proxy.plugin_driver is None:
                    raise ValueError("Record provider must be initialized.")
                self.plugin_proxy.plugin_driver.initialize_plugin()
                self.plugin_proxy.initialized = True

            if not self.plugin_proxy.failure_occurred:
                if self.plugin_proxy.plugin_driver is None:
                    raise ValueError("Record provider must be initialized.")
                self.plugin_proxy.plugin_driver.initialize_connection(connection)

        except Exception as e:
            self.plugin_proxy.handle_plugin_error(e)

    @abstractmethod
    def record_received_callback(
        self, connection: ConnectionInterface, **_: Any
    ) -> None:
        """Run callback for when a record is received."""
        pass

    @abstractmethod
    def connection_closed_callback(self, **_: Any) -> None:
        """Run callback for connection closing."""
        pass


class WorkflowRunConnectionCallbackStrategy(ConnectionCallbackStrategy):
    """Callback strategy for workflow runs."""

    def record_received_callback(
        self, connection: ConnectionInterface, **_: Any
    ) -> None:
        """Process single records by batch size."""
        batch_size = connection.record_batch_size

        if batch_size is None:
            return

        if (
            len(connection.record_containers[0].records) >= batch_size
            and not self.plugin_proxy.failure_occurred
        ):
            try:
                if self.plugin_proxy.plugin_driver is None:
                    raise ValueError("Record provider must be initialized.")
                self.plugin_proxy.plugin_driver.on_record_packet(connection)

            except Exception as e:
                self.plugin_proxy.handle_plugin_error(e)

    def connection_closed_callback(self, **_: Any) -> None:
        """Process any remaining records and finalize."""
        if (
            self.plugin_proxy.all_connections_closed
            and not self.plugin_proxy.failure_occurred
        ):
            try:
                if self.plugin_proxy.plugin_driver is None:
                    raise ValueError("Record provider must be initialized.")
                for anchor in self.plugin_proxy.input_anchors:
                    for connection in anchor.connections:
                        if any(
                            len(container.records) > 0
                            for container in connection.record_containers
                        ):
                            self.plugin_proxy.plugin_driver.on_record_packet(connection)
                self.plugin_proxy.plugin_driver.on_complete()
                self.plugin_proxy.close_output_anchors()

            except Exception as e:
                self.plugin_proxy.handle_plugin_error(e)


class UpdateOnlyConnectionCallbackStrategy(ConnectionCallbackStrategy):
    """Callback strategy for update only runs."""

    def record_received_callback(
        self, connection: ConnectionInterface, **_: Any
    ) -> None:
        """Raise error since this should never be called in update only mode."""
        raise RuntimeError("Record received in update only mode.")

    def connection_closed_callback(self, **_: Any) -> None:
        """Close all anchors."""
        if (
            self.plugin_proxy.all_connections_closed
            and not self.plugin_proxy.failure_occurred
        ):
            try:
                self.plugin_proxy.close_output_anchors()
            except Exception as e:
                self.plugin_proxy.handle_plugin_error(e)
