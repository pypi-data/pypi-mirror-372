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
"""Configurations for managing the workspace."""
import copy
import json
import os
import shutil
import string
import xml.etree.ElementTree as Et
from pathlib import Path
from typing import Any, Dict, List

from ayx_python_sdk.cli.utilities import get_install_dir
from ayx_python_sdk.cli.yxi_builder import YxiBuilder

from pydantic import BaseModel

import xmltodict


WORKSPACE_CONFIGURATION_FILE_NAME = "ayx_workspace.json"


class WorkspaceError(Exception):
    """Exception for workspace errors."""

    pass


class Workspace(BaseModel):
    """Class that wraps all workspace configurations and handles basic workspace functions."""

    workspace_dir: Path
    tools: List[str]
    yxi_name: str
    tool_family_name: str

    @classmethod
    def build_workspace(
        cls, workspace_directory: Path, allow_creation: bool = False
    ) -> "Workspace":
        """Create a workspace instance that wraps the configurations for the given workspace_directory."""
        if not workspace_directory.is_dir():
            if allow_creation:
                Workspace._create_workspace_directory(workspace_directory)
            else:
                raise WorkspaceError("Workspace directory not found.")

        workspace_config_path = workspace_directory / WORKSPACE_CONFIGURATION_FILE_NAME

        if not workspace_config_path.exists():
            raise WorkspaceError(
                "ERROR: Specified workspace_directory isn't a workspace directory, "
                f"since a {WORKSPACE_CONFIGURATION_FILE_NAME} file doesn't exist."
                "Please use an existing workspace, or specify a directory that doesn't exist yet."
            )

        with open(
            str(workspace_directory / WORKSPACE_CONFIGURATION_FILE_NAME), "r"
        ) as f:
            raw_data = json.load(f)
            migrated_data = cls.migrate_raw_workspace_config(raw_data)

            workspace = cls(workspace_dir=workspace_directory, **migrated_data)

            if migrated_data != raw_data:
                workspace.write()

            return workspace

    @classmethod
    def _create_workspace_directory(cls, workspace_directory: Path) -> None:
        """Copy the base configs to the tool directory."""
        cls._copy_base_workspace_config(workspace_directory)

        workspace = cls(
            workspace_dir=workspace_directory,
            yxi_name=workspace_directory.resolve().name,
            tool_family_name=workspace_directory.resolve().name,
            tools=[],
        )
        workspace.write()

    @staticmethod
    def _copy_base_workspace_config(workspace_directory: Path) -> None:
        install_dir = get_install_dir()
        shutil.copytree(
            str(install_dir / "assets" / "base_tool_config"),
            str(workspace_directory),
        )
        shutil.copy(
            str(install_dir / "examples" / "requirements.txt"),
            str(workspace_directory),
        )

    @classmethod
    def migrate_raw_workspace_config(cls, data: Dict) -> Dict:
        """Migrate raw JSON from old format to new format."""
        migrated_data = copy.deepcopy(data)

        if "tools" in data:
            tools = migrated_data["tools"]

            if not isinstance(tools, list):
                raise WorkspaceError(
                    "tools field in config file not properly formatted."
                )

            migrated_data["tools"] = [cls._migrate_tool(tool) for tool in tools]
        else:
            migrated_data["tools"] = []

        return migrated_data

    @staticmethod
    def _migrate_tool(tool: Any) -> str:
        # We migrated from a tools object, to just a simple list of tool names
        if isinstance(tool, str):
            return tool

        if isinstance(tool, dict):
            if "name" not in tool:
                raise WorkspaceError(
                    f"Couldn't find tool name in tool {tool} during migration."
                )

            name: str = tool["name"]
            return name

        raise WorkspaceError(
            f"Couldn't parse tool {tool} during migration. "
            "It should be a string, or an object with a 'name' key"
        )

    def add_tool_from_template(self, tool_name: str, template_tool_name: str) -> None:
        """Add a tool to the workspace."""
        tool_name_without_whitespace = remove_whitespace(tool_name)

        if not tool_name_without_whitespace.isalnum():
            raise WorkspaceError(f"The tool name is not alpha numeric: {tool_name}.")

        new_tool_directory = (
            self.workspace_dir / tool_name_without_whitespace
        ).resolve()
        if new_tool_directory.is_dir():
            raise WorkspaceError(
                f"The plugin '{tool_name_without_whitespace}' already exists in the workspace."
            )

        example_tool_directory = get_install_dir() / "examples" / template_tool_name
        shutil.copytree(str(example_tool_directory), str(new_tool_directory))

        self._update_config_file(template_tool_name, tool_name)
        self._update_main_py(template_tool_name, tool_name_without_whitespace)

        self.tools.append(tool_name_without_whitespace)
        self.write()

    def _update_config_file(self, example_tool_name: str, new_tool_name: str) -> None:
        new_tool_name_no_whitespace = remove_whitespace(new_tool_name)
        old_config_path = (
            self.workspace_dir
            / new_tool_name_no_whitespace
            / f"{example_tool_name}Config.xml"
        )
        new_config_path = (
            old_config_path.parent / f"{new_tool_name_no_whitespace}Config.xml"
        )

        os.rename(str(old_config_path), str(new_config_path))

        with open(str(new_config_path)) as f:
            config = xmltodict.parse(f.read())

        config["AlteryxJavaScriptPlugin"]["Properties"]["MetaInfo"][
            "Name"
        ] = new_tool_name

        with open(str(new_config_path), "w") as f:
            f.write(xmltodict.unparse(config, pretty=True))

    def _update_main_py(self, example_tool_name: str, new_tool_name: str) -> None:
        """Update the name of the tool in the main.py file."""
        main_filepath = self.workspace_dir / new_tool_name / "main.py"
        with open(str(main_filepath), "r") as f:
            content = f.read()

        content = content.replace(example_tool_name, new_tool_name)
        with open(str(main_filepath), "w") as f:
            f.write(content)

    def delete_tool(self, tool_name: str) -> None:
        """Remove a tool from the workspace."""
        tool_name_without_whitespace = remove_whitespace(tool_name)
        if tool_name_without_whitespace not in self.tools:
            raise WorkspaceError(
                f"No tool folder found for {tool_name_without_whitespace}"
            )

        tool_path = self.workspace_dir / tool_name_without_whitespace
        shutil.rmtree(tool_path, ignore_errors=True)
        self.tools.remove(tool_name_without_whitespace)
        self.write()

    def build_yxi(
        self, output_yxi_path: Path, package_requirements: bool = True
    ) -> None:
        """Build a YXI for the workspace."""
        if not self.tools:
            raise WorkspaceError("No tools have been added yet.")

        self._set_tool_family()
        YxiBuilder(
            self.workspace_dir, output_yxi_path, self.tools[0], package_requirements
        ).build_yxi()

    def _set_tool_family(self) -> None:
        """Ensure the workspace Config.xml and sub tools contains the tool family."""
        xml_paths = [self.workspace_dir / "Config.xml"] + [
            self.workspace_dir / tool / f"{tool}Config.xml" for tool in self.tools
        ]

        for path in xml_paths:
            with open(str(path), "r") as config_file:
                tree = Et.parse(config_file)
                root_node = tree.getroot()
                engine_settings = root_node.find("EngineSettings")

                if engine_settings is None:
                    raise ValueError("Config XML doesn't contain EngineSettings tag.")

            engine_settings.attrib["ToolFamily"] = self.tool_family_name
            tree.write(str(path))

    def write(self) -> None:
        """Write the workspace configurations to the workspace directory."""
        workspace_config_path = self.workspace_dir / WORKSPACE_CONFIGURATION_FILE_NAME
        with open(str(workspace_config_path), "w") as workspace_config_file:
            workspace_config_file.write(
                self.json(
                    exclude={
                        "workspace_dir": ...,
                        "tools": {"__all__": {"ToolDirectory"}},
                    },
                    indent=2,
                )
            )


def remove_whitespace(s: str) -> str:
    """Remove whitespace from a string."""
    for whitespace_char in string.whitespace:
        s = s.replace(whitespace_char, "")

    return s
