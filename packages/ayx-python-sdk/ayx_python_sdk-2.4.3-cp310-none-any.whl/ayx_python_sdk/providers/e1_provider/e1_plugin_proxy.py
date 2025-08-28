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
"""Base plugin definition."""
import logging
import os
import sys
from pathlib import Path
from typing import List, NoReturn, Optional, TYPE_CHECKING, Type

import AlteryxPythonSDK as Sdk

from ayx_python_sdk.core.exceptions import (
    AnchorNotFoundException,
    WorkflowRuntimeError,
)
from ayx_python_sdk.core.observable_mixin import ObservableMixin
from ayx_python_sdk.providers.e1_provider.anchor_builder import AnchorBuilder
from ayx_python_sdk.providers.e1_provider.connection_callback_strategy import (
    UpdateOnlyConnectionCallbackStrategy,
    WorkflowRunConnectionCallbackStrategy,
)
from ayx_python_sdk.providers.e1_provider.connection_interface import (
    ConnectionInterface,
    ConnectionStatus,
)
from ayx_python_sdk.providers.e1_provider.e1_environment import E1Environment
from ayx_python_sdk.providers.e1_provider.e1_input_anchor_proxy import (
    E1InputAnchorProxy,
)
from ayx_python_sdk.providers.e1_provider.e1_io import E1IO
from ayx_python_sdk.providers.e1_provider.e1_output_anchor_proxy import (
    E1OutputAnchorProxy,
)
from ayx_python_sdk.providers.e1_provider.e1_plugin_driver import E1PluginDriver
from ayx_python_sdk.providers.e1_provider.e1_provider import E1Provider
from ayx_python_sdk.providers.e1_provider.events import (
    ConnectionEvents,
    PluginEvents,
)
from ayx_python_sdk.providers.e1_provider.tool_config_loader import ToolConfigLoader
from ayx_python_sdk.providers.e1_provider.workflow_config import WorkflowConfiguration

if TYPE_CHECKING:
    from ayx_python_sdk.core.plugin import Plugin  # noqa: F401
    from ayx_python_sdk.providers.e1_provider.connection_callback_strategy import (
        ConnectionCallbackStrategy,
    )


class E1PluginProxy(ObservableMixin):
    """Base plugin to inherit from."""

    __slots__ = [
        "tool_id",
        "anchor_builder",
        "input_anchors",
        "output_anchors",
        "workflow_config",
        "failure_occurred",
        "initialized",
        "record_batch_size",
        "plugin_driver",
        "engine",
        "user_plugin",
        "tool_config_loader",
        "_output_anchor_mgr",
        "__environment",
        "__io",
        "__input_connections",
    ]

    user_plugin_class: Type["Plugin"]
    user_plugin_directory_name: str

    def __init__(
        self,
        tool_id: int,
        alteryx_engine: Sdk.AlteryxEngine,
        output_anchor_mgr: Sdk.OutputAnchorManager,
    ):
        """Construct a plugin."""
        ObservableMixin.__init__(self)
        self.tool_id = tool_id
        self.engine = alteryx_engine
        self._output_anchor_mgr = output_anchor_mgr
        self.initialized = False
        self.failure_occurred = False
        self.__environment = E1Environment(alteryx_engine, tool_id, self)
        self.__io = E1IO(alteryx_engine, tool_id)
        self.__input_connections: List = []

        self.configure_logger()

        # These properties should be assigned before pi_init gets called
        self.record_batch_size: Optional[int] = None

        # These properties get assigned in pi_init
        self.anchor_builder: Optional[AnchorBuilder] = None
        self.workflow_config = WorkflowConfiguration("<Configuration/>")
        self.input_anchors: List[E1InputAnchorProxy] = []
        self.output_anchors: List[E1OutputAnchorProxy] = []
        self.plugin_driver: Optional[E1PluginDriver] = None
        self.tool_config_loader = ToolConfigLoader(self.user_plugin_directory_name)

    def pi_init(self, workflow_config_xml_string: str) -> None:
        """Plugin initialization from the engine."""
        if self.tool_name is None:
            raise ValueError("Name must be set before plugin can be used.")

        # DO NOT REMOVE NEXT LINE: The base SDK has issues with sys.path updates,
        # and in order to fix some dependency resolution issues we have to update it again here
        self.update_sys_path()

        self.anchor_builder = AnchorBuilder(
            self.tool_config_loader.get_tool_config(), self._output_anchor_mgr
        )
        self.workflow_config = WorkflowConfiguration(workflow_config_xml_string)
        self.input_anchors = self.anchor_builder.build_input_anchors()
        self.output_anchors = self.anchor_builder.build_output_anchors()
        self.notify_topic(PluginEvents.PLUGIN_INITIALIZED)
        self.plugin_driver = E1PluginDriver(
            self.user_plugin_class, E1Provider(self, self.workflow_config)
        )

    def pi_add_incoming_connection(
        self, anchor_name: str, connection_name: str
    ) -> ConnectionInterface:
        """Add incoming connection to the tool from the engine."""
        anchor = [a for a in self.input_anchors if a.name == anchor_name][0]

        connection = ConnectionInterface(self, connection_name, anchor)
        anchor.connections.append(connection)
        self._subscribe_to_connection(connection)
        return connection

    def _subscribe_to_connection(self, connection: ConnectionInterface) -> None:
        """Subscribe to events of interest generated by a connection."""
        connection.subscribe(
            ConnectionEvents.CONNECTION_INITIALIZED,
            self.callback_strategy.connection_initialized_callback,
        )
        connection.subscribe(
            ConnectionEvents.RECORD_RECEIVED,
            self.callback_strategy.record_received_callback,
        )
        connection.subscribe(
            ConnectionEvents.CONNECTION_CLOSED,
            self.callback_strategy.connection_closed_callback,
        )
        connection.subscribe(
            ConnectionEvents.PROGRESS_UPDATE,
            self.callback_strategy.update_progress_callback,
        )

    def pi_add_outgoing_connection(self, anchor_name: str) -> bool:
        """Register an outgoing connection from this tool."""
        anchor = [a for a in self.output_anchors if a.name == anchor_name][0]
        anchor.num_connections += 1
        return True

    def pi_push_all_records(self, n_record_limit: int) -> bool:
        """Push all records when no inputs are connected."""
        try:
            if len(self.required_input_anchors) == 0:
                if self.plugin_driver is None:
                    raise ValueError("Record provider must be initialized.")
                self.plugin_driver.initialize_plugin()
                self.initialized = True

                if not self.environment.update_only:
                    self.plugin_driver.on_complete()

                self.close_output_anchors()
                return True

            self.raise_missing_inputs()
        except Exception as e:
            self.handle_plugin_error(e)

        return False

    def raise_missing_inputs(self) -> NoReturn:
        """Send a missing incoming inputs error to Designer."""
        raise WorkflowRuntimeError(self.engine.xmsg("Missing Incoming Connection(s)."))

    def pi_close(self, b_has_errors: bool) -> None:
        """Cleans-up resources, flushes and closes logger's handlers."""
        logger = self.logger
        for handler in logger.handlers:
            logger.removeHandler(handler)
            handler.flush()
            handler.close()

    def configure_logger(self) -> None:
        """Configure the logger."""
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

        file_handler = logging.FileHandler(self.log_filepath)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

        self.logger.setLevel(logging.INFO)

    def handle_plugin_error(self, e: Exception) -> None:
        """Log a plugin error to the log and a generic error to Designer."""
        logger = self.logger

        if isinstance(e, WorkflowRuntimeError):
            logger.error(str(e))
            self.io.error(str(e))
        else:
            logger.exception(e)
            self.io.error(
                f"Unexpected error occurred in plugin please see log file: {str(self.log_filepath)}"
            )
        self.failure_occurred = True
        self.notify_topic(PluginEvents.PLUGIN_FAILURE, exception=e)

    def push_all_metadata(self) -> None:
        """Push all metadata for anchors."""
        for anchor in self.output_anchors:
            anchor.push_metadata()

    def close_output_anchors(self) -> None:
        """Close connection for all output anchors."""
        for anchor in self.output_anchors:
            anchor.close()

    def get_input_anchor(self, input_anchor_name: str) -> E1InputAnchorProxy:
        """Get an input anchor by name."""
        try:
            return [
                anchor
                for anchor in self.input_anchors
                if anchor.name == input_anchor_name
            ][0]
        except IndexError:
            raise AnchorNotFoundException(f"{input_anchor_name} not found.")

    def get_output_anchor(self, output_anchor_name: str) -> E1OutputAnchorProxy:
        """Get an output anchor by name."""
        try:
            return [
                anchor
                for anchor in self.output_anchors
                if anchor.name == output_anchor_name
            ][0]
        except IndexError:
            raise AnchorNotFoundException(f"{output_anchor_name} not found.")

    def update_sys_path(self) -> None:
        """
        Update the sys.path to fix SDK issues.

        The sys.path must be updated to include:
        - The venv path
        - The tool directory

        in order for inline imports to work due to base SDK sys.path manipulation issues.
        """
        install_metadata = self.tool_config_loader.get_tool_install_metadata()

        for path in [
            install_metadata.venv_path / "Lib" / "site-packages",
            install_metadata.install_path,
        ]:
            sys.path.append(str(path))

    @property
    def tool_name(self) -> str:
        """Getter for the tool name."""
        return self.user_plugin_class.__name__

    @property
    def callback_strategy(self) -> "ConnectionCallbackStrategy":
        """Generate the callback strategy for the tool."""
        return (
            UpdateOnlyConnectionCallbackStrategy(self)
            if self.environment.update_only
            else WorkflowRunConnectionCallbackStrategy(self)
        )

    @property
    def log_directory(self) -> Path:
        """Get the log directory."""
        if sys.platform == "win32":
            log_directory = Path(os.environ["localappdata"]) / "Alteryx" / "Log"
        else:
            # Required for CI/CD pipelines running in linux environment
            # + future proofing
            log_directory = Path.home() / ".Alteryx" / "Log"

        log_directory.mkdir(parents=True, exist_ok=True)
        return log_directory

    @property
    def log_filepath(self) -> Path:
        """Get the log filename."""
        return self.log_directory / f"{self.tool_name}{self.tool_id}.log"

    @property
    def all_required_connections_connected(self) -> bool:
        """Getter that indicates if all required connections are connected."""
        return all(
            [len(anchor.connections) > 0 for anchor in self.required_input_anchors]
        )

    @property
    def all_connections_initialized(self) -> bool:
        """Getter that indicates if all input connections are initialized."""
        return all(
            [
                connection.status != ConnectionStatus.CREATED
                for anchor in self.input_anchors
                for connection in anchor.connections
            ]
        )

    @property
    def all_connections_closed(self) -> bool:
        """Getter that indicates if all input connections are closed."""
        return all(
            [
                connection.status == ConnectionStatus.CLOSED
                for anchor in self.input_anchors
                for connection in anchor.connections
            ]
        )

    @property
    def required_input_anchors(self) -> List[E1InputAnchorProxy]:
        """Get the list of required input anchors for this tool."""
        return [anchor for anchor in self.input_anchors if not anchor.optional]

    @property
    def logger(self) -> logging.Logger:
        """Get logger."""
        return logging.getLogger(f"{self.tool_name}{self.tool_id}")

    @property
    def io(self) -> E1IO:
        """Get the IO object from this provider."""
        return self.__io

    @property
    def environment(self) -> E1Environment:
        """Get the Environment object from this provider."""
        return self.__environment
