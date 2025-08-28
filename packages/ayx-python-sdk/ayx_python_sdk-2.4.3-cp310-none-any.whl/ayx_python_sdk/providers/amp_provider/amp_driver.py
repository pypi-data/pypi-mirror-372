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
"""AMP Driver class definition."""
import asyncio
import logging
import traceback
from typing import Any, Callable, NamedTuple, Optional, TYPE_CHECKING

from ayx_python_sdk.core import PluginV2
from ayx_python_sdk.core.exceptions import WorkflowRuntimeError
from ayx_python_sdk.core.input_connection_base import InputConnectionStatus
from ayx_python_sdk.providers.amp_provider.amp_io_components import (
    ControlIOBuffer,
    StreamIOBuffer,
)
from ayx_python_sdk.providers.amp_provider.amp_provider_v2 import AMPProviderV2
from ayx_python_sdk.providers.amp_provider.logger_config import get_plugin_logger
from ayx_python_sdk.providers.amp_provider.repositories import (
    InputRecordPacketRepository,
    Singleton,
)
from ayx_python_sdk.providers.amp_provider.repositories.input_record_packet_repository import (
    EmptyRecordPacketRepositoryException,
    InputConnectionRepository,
    UnfinishedRecordPacketException,
)


if TYPE_CHECKING:
    from ayx_python_sdk.providers.amp_provider.resources.generated.sdk_tool_service_v2_pb2 import (
        ControlIn,
    )
    from ayx_python_sdk.providers.amp_provider.amp_environment_v2 import (
        AMPEnvironmentV2,
    )
    import pyarrow as pa

logger = logging.getLogger(__name__)


class AMPDriver(metaclass=Singleton):
    """The AMP Driver is a class that manages the lifecycle methods of a plugin instance."""

    def __init__(self) -> None:
        self.__plugin: Optional["PluginV2"] = None
        self.anchors: dict = {"incoming": {}, "outgoing": {}}
        self.provider: AMPProviderV2 = AMPProviderV2()
        self._plugin_class: Optional[Callable] = None
        self.event_plugin_complete = asyncio.Event()
        self.event_notify_on_complete = asyncio.Event()

    def _handle_all_errors(self, exception: Exception) -> None:
        traceback_list = traceback.format_tb(exception.__traceback__)
        traceback_string = "".join(["\n"] + traceback_list[1:])
        amp_logger = self.provider.logger
        amp_logger.exception(traceback_string)

    def _run_with_error_handling(self, _callable: Callable, *args: Any) -> None:
        try:
            _callable(*args)
        except (Exception, WorkflowRuntimeError) as e:
            self.provider.io.error(f"{type(e)}: {e}")
            self._handle_all_errors(e)

    def run_user_init(self) -> None:
        """Allow running plugin's init in a non-blocking executor."""
        try:
            self.plugin = self._plugin_class(self.provider)  # type: ignore
        except Exception as e:
            self.ctrl_io.error(f"Could not init plugin {repr(e)}")
        logger.info("Loaded and init user plugin")

    async def _initialize_plugin(
        self,
        _init_data: "ControlIn",
        ready_for_records: asyncio.Event,
        record_batch_received: asyncio.Event,
    ) -> bool:
        logger.debug("Starting plugin init")
        # Wait until client sends the init data, ctrl_read will set it then
        request = _init_data
        self.provider.set_anchors(request)
        self.provider.environment.set_tool_config(
            request.plugin_initialization_data.configXml
        )
        self.provider.environment.save_engine_constants(
            dict(request.plugin_initialization_data.engineConstants)
        )
        logger.debug("AMP CONSTANTS:")
        logger.debug(f"Designer Version: {self.provider.environment.designer_version}")
        logger.debug(
            f"Alteryx Install Directory: {self.provider.environment.alteryx_install_dir}"
        )
        logger.debug(f"Workflow Directory: {self.provider.environment.workflow_dir}")
        logger.debug(f"Temp Directory: {self.provider.environment.temp_dir}")
        logger.debug(f"Tool ID: {self.provider.environment.tool_id}")
        logger.debug(f"Workflow ID: {self.provider.environment.workflow_id}")
        logger.debug(f"Raw Constants: {self.provider.environment.raw_constants}")
        self.provider.environment.save_update_mode(
            request.plugin_initialization_data.updateMode
        )

        # TODO: Check and see if we actually need these - we already set anchors upstream
        for anchor in request.plugin_initialization_data.incomingAnchors:
            self.anchors["incoming"][anchor.name] = anchor
        for anchor in request.plugin_initialization_data.outgoingAnchors:
            self.anchors["outgoing"][anchor.name] = anchor
        try:
            if self._plugin_class:
                log_handle = (
                    f"{self._plugin_class.__name__}.{self.provider.environment.tool_id}"
                )
                logger.debug("Creating log file %s\n", log_handle)
                self.provider.logger = get_plugin_logger(
                    log_handle, self.provider.environment.get_log_directory()
                )
        except Exception as e:
            err_str = """
            Could not dynamically create named plugin logger! \n
            %s
            If you are using custom logging and seeing this error, setting
             your plugin logger during the plugin's __init__ may resolve this warning.
            """
            logger.warn(err_str, repr(e))
        try:
            init_plugin_event = self.ctrl_io.push_driver_callback(self.run_user_init)
            await init_plugin_event.wait()
            ready_for_records.set()
            if (
                len(self.anchors["incoming"]) == 0
                or self.provider.environment.update_only
            ):
                logger.debug("tool has no input anchors")
                logger.debug("setting record_batch_received signal")
                record_batch_received.set()
            logger.debug(
                "done waiting for plugin init, signal RecordTransfer stream is ready to process record batches..."
            )
            self.ctrl_io.info("Plugin class successfully loaded.")
        except Exception as e:
            logger.error("Exception placing plugin init on action queue: %s", repr(e))
            return False

        # We can't guarantee this is initialized until after this. But,
        # TracerBullet code suggests translate_msg should be callable in __init__
        # for a plugin
        return True

    def metadata_received(self, anchor_name: str, connection_name: str) -> None:
        """
        Retrieve the input connection, and call plugin's on_input_connection_initialized method.

        Parameters
        ----------
        anchor_name: str
            The name of the input anchor associated with the connection to be initialized.

        connection_name: str
            The name of the input connection to be retrieved.
        """
        connection = InputConnectionRepository().get_connection(
            anchor_name, connection_name
        )

        InputConnectionRepository().save_connection_status(
            anchor_name, connection_name, InputConnectionStatus.INITIALIZED
        )
        logger.debug("Connection %s on %s initialized", connection_name, anchor_name)
        self._run_with_error_handling(
            self.plugin.on_input_connection_opened, connection
        )

    def record_packet_received(self, anchor_name: str, connection_name: str) -> None:
        """
        Retrieve input connection, and call plugin's on_record_packet method.

        Parameters
        ----------
        anchor_name: str
            The name of the input anchor associated with the connection to be read from.

        connection_name: str
            The name of the input connection to be retrieved.
        """
        connection = InputConnectionRepository().get_connection(
            anchor_name, connection_name
        )
        InputConnectionRepository().save_connection_status(
            anchor_name, connection_name, InputConnectionStatus.RECEIVING_RECORDS
        )
        logger.debug(
            "Connection %s on anchor %s receiving records", connection_name, anchor_name
        )
        while True:
            try:
                InputRecordPacketRepository().peek_record_packet(
                    anchor_name, connection_name
                )
            except (
                UnfinishedRecordPacketException,
                EmptyRecordPacketRepositoryException,
            ):
                break
            else:
                logger.debug(
                    "Sending record packet to connection %s on anchor %s",
                    connection_name,
                    anchor_name,
                )
                self._run_with_error_handling(self.plugin.on_record_packet, connection)
                InputRecordPacketRepository().pop_record_packet(
                    anchor_name, connection_name
                )

    def incoming_connection_complete_callback(self, anchor: NamedTuple) -> None:
        """
        Will call when an incoming connection is done sending RecordBatches.

        Parameters
        ----------
        anchor_name: The name of the anchor.
        connection_name: The name of the connection.
        """
        self._run_with_error_handling(
            self.plugin.on_incoming_connection_complete, anchor
        )

    def record_batch_received(self, record_msg: "pa.Table", anchor: NamedTuple) -> None:
        """
        Handle received batch and call plugin's on_record_batch if a full record is ready.

        Parameters
        ----------
        record_msg: An IncomingRecords message
        """
        logger.debug("Calling plugin's on_record_batch")
        self._run_with_error_handling(self.plugin.on_record_batch, record_msg, anchor)

    def connection_closed_callback(
        self, anchor_name: str, connection_name: str
    ) -> None:
        """
        Close individual connections.

        Parameters
        ----------
        anchor_name: str
            The name of the input anchor associated with the connection to be closed.

        connection_name: str
            The name of the input connection to be closed.
        """
        InputConnectionRepository().save_connection_status(
            anchor_name, connection_name, InputConnectionStatus.CLOSED
        )
        logger.debug("Closed connection %s on anchor %s", connection_name, anchor_name)
        try:
            InputRecordPacketRepository().peek_record_packet(
                anchor_name, connection_name
            )
        except EmptyRecordPacketRepositoryException:
            pass
        except ValueError:
            logger.debug(
                "%s was not found in the InputRecordPacketRepository. (There were no records associated with this anchor.)",
                anchor_name,
            )
        else:
            self._run_with_error_handling(
                self.plugin.on_record_packet,
                InputConnectionRepository().get_connection(
                    anchor_name, connection_name
                ),
            )

    def on_complete_callback(self) -> None:
        """Call plugin's on_complete method."""
        logger.debug("Running plugin's on_complete")
        self._run_with_error_handling(self.plugin.on_complete)
        logger.debug("Plugin complete, closing")

    @property
    def plugin(self) -> "PluginV2":
        """
        Get the plugin associated with this driver.

        Returns
        -------
        Plugin
            The plugin associated with this AMP Driver instance.

        Raises
        ------
        ValueError
            If the plugin hasn't been assigned.
        """
        if self.__plugin is None:
            raise ValueError("Plugin cannot be None")

        return self.__plugin

    @plugin.setter
    def plugin(self, value: "PluginV2") -> None:
        """
        Set the plugin associated with this driver.

        Parameters
        ----------
        value: Plugin
            The plugin to be assigned.

        """
        self.__plugin = value
        logger.debug("Assigned plugin %s", value)

    """
    These properties are aiming to improve readability/show intent and avoid
    confusing 'pass by object' behaviour. We can remove if others don't agree.
    If we haven't loaded the user's plugin class yet, we'll return what will
    eventually be passed. Once we've passed the provider obj to the plugin,
    we'll, semantically at least, then pass over ownership.
    """

    @property
    def ctrl_io(self) -> "ControlIOBuffer":
        """Get the plugin provider's io buffer, convenience property."""
        if self.__plugin is None:
            return self.provider.io
        return self.__plugin.provider.io

    @property
    def record_io(self) -> "StreamIOBuffer":
        """Get plugin providers record buffer, convenience property."""
        if self.__plugin is None:
            return self.provider.record_io
        return self.__plugin.provider.record_io

    @property
    def environment(self) -> "AMPEnvironmentV2":
        """Get plugin provider's environment."""
        if self.__plugin is None:
            self.provider.environment
        return self.__plugin.provider.environment  # type: ignore

    def clear_state(self) -> None:
        """Reset the AMP Driver."""
        self.__plugin = None
