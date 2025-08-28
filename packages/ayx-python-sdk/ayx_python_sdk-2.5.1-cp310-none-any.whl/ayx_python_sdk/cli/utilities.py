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
"""Helper methods for managing the virtual environment."""
import os
import xml.etree.ElementTree as Et
from pathlib import Path
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ayx_python_sdk.cli.workspace import Workspace  # noqa: F401


def get_install_dir() -> Path:
    """Get the current directory."""
    return Path(__file__).parent.parent


def environment_requires_update(workspace: "Workspace") -> bool:
    """Determine if the virtual environments for the tools should be updated."""
    if not _virtual_environment_exists(workspace.tool_family_name):
        return True

    if not workspace.tools:
        return False

    tool_family_requirements_path = (
        Path(_get_alteryx_tools_path()) / workspace.tools[0] / "requirements.txt"
    )

    if not tool_family_requirements_path.is_file():
        return True

    workspace_requirements = _get_requirements(
        workspace.workspace_dir / "requirements.txt"
    )
    installed_tool_family_requirements = _get_requirements(
        tool_family_requirements_path
    )
    return workspace_requirements != installed_tool_family_requirements


def get_alteryx_path() -> Path:
    """Get the path to Alteryx Designer."""
    user_designer_install_path = Path(os.getenv("LOCALAPPDATA", "")) / "Alteryx"
    user_designer_engine_cmd_path = (
        user_designer_install_path / "bin" / "AlteryxEngineCmd.exe"
    )
    if user_designer_engine_cmd_path.exists():
        return user_designer_install_path

    admin_designer_install_path = Path(os.getenv("PROGRAMFILES", "")) / "Alteryx"
    admin_designer_engine_cmd_path = (
        admin_designer_install_path / "bin" / "AlteryxEngineCmd.exe"
    )
    if admin_designer_engine_cmd_path.exists():
        return admin_designer_install_path

    raise FileNotFoundError("Alteryx Install Path could not be located.")


def get_tool_family_attribute_from_config(config_xml_path: Path) -> str:
    """Get the ToolFamily attribute from the Config.xml file."""
    with open(str(config_xml_path), "r") as config_file:
        tree = Et.parse(config_file)
        root_node = tree.getroot()
        engine_settings = root_node.find("EngineSettings")
        if engine_settings is None:
            raise ValueError("Config xml doesn't contain engine settings.")

        tool_family = str(engine_settings.attrib["ToolFamily"])
        return tool_family


def _get_alteryx_tools_path() -> Path:
    """Get the path to the Alteryx Tools folder (for 3P plugins)."""
    user_install_path = Path(os.getenv("APPDATA", "")) / "Alteryx" / "Tools"
    return user_install_path


def _get_requirements(requirements_path: Path) -> List[str]:
    """Get the workspace level requirements file."""
    with open(str(requirements_path), "r") as req_file:
        requirements = req_file.readlines()

    return [line for line in requirements if "--find-links" not in line]


def _virtual_environment_exists(tool_family_name: str) -> bool:
    """Check if the virtual environment exists."""
    venv_name = f"{tool_family_name}_venv"
    designer_venv_path = Path(_get_alteryx_tools_path()) / venv_name
    return designer_venv_path.is_dir()
