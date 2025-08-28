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
"""Proxy Class for managing the SDK environment on Alteryx Multi-threaded Processing (AMP)."""
import logging
import os
import sys
import uuid
from pathlib import Path
from typing import Dict, Optional

from ayx_python_sdk.core.doc_utilities import inherit_docs
from ayx_python_sdk.core.environment_base import EnvironmentBase, Locale, UpdateMode
from ayx_python_sdk.core.exceptions import WorkflowRuntimeError
from ayx_python_sdk.providers.amp_provider.resources.generated.plugin_initialization_data_pb2 import (
    UpdateMode as Protobuf_UpdateMode,
)

import xmltodict

logger = logging.getLogger()


@inherit_docs
class AMPEnvironmentV2(EnvironmentBase):
    """Variables that describe the Designer environment when AMP is enabled."""

    tool_config: Dict = {}

    def __init__(self) -> None:
        self._update_mode: Optional[UpdateMode] = None
        self._update_only: Optional[bool] = None
        self._proxy_configuration: Dict[str, str] = {}
        self._workflow_id: str = ""
        self._tool_id: int = 0
        self.raw_constants: Dict[str, str] = {}

    @property
    def update_only(self) -> bool:  # noqa: D102
        if self._update_only is None:
            raise RuntimeError("Update Only has not been determined yet.")
        return self._update_only

    @property
    def update_mode(self) -> "UpdateMode":  # noqa: D102
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

    @property
    def designer_version(self) -> str:  # noqa: D102
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

    @property
    def workflow_dir(self) -> "Path":  # noqa: D102
        """
        Get the directory where the workflow is running the tool.

        Returns
        -------
        Path
            The workflow directory as a Path object.
        """
        if self._workflow_dir is None:
            raise RuntimeError(
                "Environment repository has not received the 'worklfow_dir' engine constant yet."
            )
        return self._workflow_dir

    @property
    def workflow_id(self) -> str:  # noqa: D102
        """
        Get the WorkflowRunGuid for the currently-running workflow.

        Returns
        -------
        str
            The workflow id.
        """
        return self._workflow_id

    @property
    def alteryx_install_dir(self) -> "Path":  # noqa: D102
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

    @property
    def temp_dir(self) -> str:
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

    @property
    def alteryx_locale(self) -> "Locale":  # noqa: D102
        """
        Get the locale code from Alteryx user settings.

        Returns
        -------
        Locale
            The language / region that Alteryx is using to display messages.
        """
        # TODO
        return "en"

    @property
    def tool_id(self) -> int:  # noqa: D102
        """
        Get the ID of the tool.

        Returns
        -------
        int
            Tool's ID (specified by developer).
        """
        return self._tool_id

    @property
    def proxy_configuration(self) -> dict:  # noqa: D102
        return self._proxy_configuration

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
            self._tool_id = int(constants.get("ToolId", 0))
            self._workflow_id = constants.get("WorkflowRunGuid", "")
            self.raw_constants = constants
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

    def set_tool_config(self, config_xml_str: str) -> None:
        """Parse an xml string to dict form and set the config."""
        self.tool_config = dict(
            xmltodict.parse(config_xml_str, strip_whitespace=False)["Configuration"]
            or {}
        )

    def parse_settings_key_value(
        self, settings_str: str, line_delimiter: str = "\n", key_delimiter: str = "="
    ) -> dict:  # noqa: D102
        return super().parse_settings_key_value(
            settings_str, line_delimiter=line_delimiter, key_delimiter=key_delimiter
        )

    def get_settings_conf(self, *args: list) -> dict:  # noqa: D102
        return super().get_settings_conf(*args)

    def update_tool_config(self, new_config: dict) -> None:  # noqa: D102
        self.tool_config = new_config

    def create_temp_file(self, extension: str = "tmp") -> "Path":  # noqa: D102
        """
        Create a temporary file managed by Designer.

        Parameters
        ----------
        extension
            The file extension of the temp file.

        Returns
        -------
        Path
            The path to where the temp file is.
        """
        temp_file_name = f"temp-file-{str(uuid.uuid4())}.{str(extension)}"
        temp_file_path = Path(self.temp_dir) / (temp_file_name)
        try:
            temp_file_path.touch()
        except FileNotFoundError:
            # path does not exist
            logger.error("Engine.TempFilePath (%s) does not exist", self.temp_dir)
        except IOError:
            # path exists but no write permissions
            logger.error("No write permissions for directory %s", self.temp_dir)
        return Path(temp_file_path)

    def get_log_directory(self) -> "Path":
        """Return the root log directory for the current platform."""
        log_directory = (
            Path(os.environ["localappdata"]) / "Alteryx"
            if sys.platform == "win32"
            else Path("/var/log")
        )
        return log_directory
