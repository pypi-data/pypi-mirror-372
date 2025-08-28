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
"""Class that saves and retrieves AMP environment information."""
import logging
from pathlib import Path
from typing import Dict, Optional, TYPE_CHECKING

from ayx_python_sdk.core.environment_base import UpdateMode
from ayx_python_sdk.core.exceptions import WorkflowRuntimeError
from ayx_python_sdk.providers.amp_provider.repositories.singleton import Singleton
from ayx_python_sdk.providers.amp_provider.resources.generated.plugin_initialization_data_pb2 import (
    UpdateMode as Protobuf_UpdateMode,
)

if TYPE_CHECKING:
    from ayx_python_sdk.core.environment_base import Locale

logger = logging.getLogger()


class EnvironmentRepository(metaclass=Singleton):
    """Repository that stores environment information."""

    def __init__(self) -> None:
        """Initialize the environment repository."""
        self._designer_version: Optional[str] = None
        self._workflow_dir: Optional[Path] = None
        self._alteryx_install_dir: Optional[Path] = None
        self._temp_dir: Optional[str] = None
        self._update_mode: Optional["UpdateMode"] = None
        self._update_only: Optional[bool] = None
        self._proxy_configuration: dict = {}

    def get_update_only(self) -> bool:
        """
        Check if the tool is running in update only mode.

        Returns
        -------
        bool
            True if workflow isn't being run.
        """
        if self._update_only is None:
            raise RuntimeError("Update Only has not been determined yet.")
        return self._update_only

    def get_update_mode(self) -> UpdateMode:
        """
        Get the type of tool update running.

        Returns
        -------
        UpdateMode
            Enum corresponding to the type of update mode designer is running in. (Quick, Full, No Update)
        """
        if self._update_mode is None:
            raise RuntimeError("Update Mode has not been determined yet.")
        return self._update_mode

    def get_designer_version(self) -> str:
        """
        Get the version of designer that is running the tool.

        Returns
        -------
        str
            A version in the format of 1.2.3.4
        """
        if self._designer_version is None:
            raise RuntimeError(
                "Environment repository has not received the 'designer_version' engine constant yet."
            )
        return self._designer_version

    def get_alteryx_install_dir(self) -> Path:
        """
        Get the directory where designer is stored.

        Returns
        -------
        Path
            The Alteryx install directory as a Path object.
        """
        if self._alteryx_install_dir is None:
            raise RuntimeError(
                "Environment repository has not received the 'alteryx_install_dir' engine constant yet."
            )
        return self._alteryx_install_dir

    def get_temp_dir(self) -> str:
        """
        Get the directory where designer-managed temp files are created.

        Returns
        -------
        str
            The path to the directory where temporary files are stored.
        """
        if self._temp_dir is None:
            raise RuntimeError(
                "Environment repository has not received the 'temp_dir' engine constant yet."
            )
        return self._temp_dir

    def get_alteryx_locale(self) -> "Locale":
        """
        Get the locale code from Alteryx user settings.

        Returns
        -------
        Locale
            The language / region that Alteryx is using to display messages.
        """
        # TODO
        return "en"

    def get_tool_id(self) -> int:
        """
        Get the ID of the tool.

        Returns
        -------
        int
            Tool's ID (specified by developer).
        """
        # TODO
        return 0

    def save_tool_config(self, new_config: dict) -> None:
        """
        Update the tool's configuration file.

        Parameters
        ----------
        new_config
            The new configuration to set for the tool.
        """
        from ayx_python_sdk.providers.amp_provider.repositories.tool_config_repository import (
            ToolConfigRepository,
        )

        ToolConfigRepository().save_tool_config(new_config)

    def get_proxy_configuration(self) -> dict:  # noqa: D102
        return self._proxy_configuration

    def save_engine_constants(self, constants: Dict[str, str]) -> None:
        """
        Save engine constants to repo.

        Parameters
        ----------
        constants
            The dictionary of engine constants received through gRPC
        """
        try:
            self._designer_version = constants["Engine.Version"]
            self._alteryx_install_dir = Path(constants["AlteryxExecutable"])
            self._workflow_dir = Path(constants["Engine.WorkflowDirectory"])
            self._temp_dir = constants["Engine.TempFilePath"]

        except KeyError:
            raise WorkflowRuntimeError(
                "One or more Engine Constants missing from dictionary."
            )
        # The proxy config keys are not always present, so technically an optional kwarg here.
        self._proxy_configuration = {}
        if constants.get("ProxyConfiguration"):
            for key_val_pair in constants["ProxyConfiguration"].split("\n"):
                keyval = key_val_pair.split("=", 1)
                # might have a blank or unset key
                if len(keyval) > 1:
                    self._proxy_configuration[keyval[0]] = keyval[1]

    def save_update_mode(self, update_mode: int) -> None:
        """
        Save the passed in update mode.

        Parameters
        ----------
        update_mode
            An int that corresponds to the protobuf enumeration for the update mode that designer is running in.
        """
        if update_mode == Protobuf_UpdateMode.UM_Run:
            self._update_mode = UpdateMode.NO_UPDATE_MODE
            self._update_only = False
        if update_mode == Protobuf_UpdateMode.UM_Full:
            self._update_mode = UpdateMode.FULL
            self._update_only = True
        if update_mode == Protobuf_UpdateMode.UM_Quick:
            self._update_mode = UpdateMode.QUICK
            self._update_only = True

    def clear_repository(self) -> None:
        """Clear the repository."""
        self._designer_version = None
        self._workflow_dir = None
        self._alteryx_install_dir = None
        self._temp_dir = None
        self._update_mode = None
        self._update_only = None
