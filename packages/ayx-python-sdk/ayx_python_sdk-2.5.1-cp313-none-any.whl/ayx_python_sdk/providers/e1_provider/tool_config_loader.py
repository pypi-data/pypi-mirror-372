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
"""Tool configuration loader definition."""
import os
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Tuple

import xmltodict


class ToolInstallType(str, Enum):
    """Tool install type enumeration."""

    user = "user"
    admin = "admin"
    alteryx = "alteryx"
    noinstall = "noinstall"  # for linux builds


class ToolInstallMetadata:
    """Tool installation metadata."""

    def __init__(
        self, install_path: Path, venv_path: Path, install_type: ToolInstallType
    ):
        self.install_path = install_path
        self.venv_path = venv_path
        self.install_type = install_type


class ToolConfigLoader:
    """Tool configuration loader definition."""

    def __init__(self, tool_directory_name: str):
        """Construct a tool configuration loader."""
        self.tool_directory_name = tool_directory_name

    def get_tool_config(self) -> Dict[str, Any]:
        """Get the tool config of this tool from its config.xml file."""
        try:
            with open(str(self.get_tool_config_filepath())) as fd:
                tool_config = dict(xmltodict.parse(fd.read(), strip_whitespace=False))
        except FileNotFoundError:
            raise RuntimeError(
                f"Couldn't find tool with name {self.tool_directory_name}."
            )
        else:
            return tool_config

    def get_tool_config_filepath(self) -> Path:
        """Get the path to the tool configuration file."""
        tool_path, _ = self._get_tool_path()
        return Path(
            os.path.join(str(tool_path), f"{self.tool_directory_name}Config.xml")
        )

    def get_tool_install_metadata(self) -> ToolInstallMetadata:
        """Get tool install metadata."""
        tool_path, install_type = self._get_tool_path()
        venv_path = self._get_tool_venv_path(
            self.get_tool_config(), tool_path, install_type
        )
        return ToolInstallMetadata(
            install_path=tool_path, venv_path=venv_path, install_type=install_type
        )

    def _get_tool_path(self) -> Tuple[Path, ToolInstallType]:
        """Get the path to the directory containing the current tool's definition."""
        tools_path, install_type = self._get_tools_location()
        return (
            Path(os.path.join(str(tools_path), self.tool_directory_name)),
            install_type,
        )

    def _get_tools_location(self) -> Tuple[Path, ToolInstallType]:
        """Get the location of Alteryx tools that contain the current tool."""
        linux_path = Path("/opt/alteryx")
        if linux_path.is_dir():
            return linux_path, ToolInstallType.noinstall

        tools_rel_path = Path("Alteryx") / "Tools"
        admin_path = Path(os.environ["ALLUSERSPROFILE"]) / tools_rel_path
        user_path = Path(os.environ["APPDATA"]) / tools_rel_path

        alteryx_bin = (
            Path(os.path.dirname(sys.executable))
            if "AlteryxEngineCmd.exe" in sys.executable
            else Path("")
        )
        html_plugins_path = alteryx_bin / "HtmlPlugins"

        for path, install_type in (
            (user_path, ToolInstallType.user),
            (admin_path, ToolInstallType.admin),
            (html_plugins_path, ToolInstallType.alteryx),
        ):
            if path.is_dir() and self.tool_directory_name in [
                child_dir.name for child_dir in path.iterdir()
            ]:
                return path, install_type

        raise RuntimeError("Tool is not located in Alteryx install locations.")

    @staticmethod
    def _get_tool_venv_path(
        config: Dict, tool_path: Path, install_type: ToolInstallType
    ) -> Path:
        """Get the path to the current tools virtual environment."""
        try:
            tool_family_name = config["AlteryxJavaScriptPlugin"]["EngineSettings"][
                "@ToolFamily"
            ]
        except KeyError:
            venv_path = tool_path
        else:
            venv_name = f"{tool_family_name}_venv"
            venv_path = tool_path / ".." / venv_name

        return venv_path.resolve()
