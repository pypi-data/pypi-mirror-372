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
"""Wrappers to handle interactions with YXI Installer."""
from pathlib import Path
from typing import List


class YxiInstaller:
    """Class that wraps install commands from the YXI Installer executable."""

    def __init__(
        self,
        yxi_paths: List[Path],
        alteryx_path: Path,
        clean: bool = False,
        update_venv: bool = False,
    ) -> None:
        if len(yxi_paths) < 1:
            raise ValueError("At least one yxi path is required for the yxi installer.")

        self.yxi_paths = yxi_paths
        self.alteryx_path = alteryx_path
        self.clean = clean
        self.update_venv = update_venv

    @staticmethod
    def _get_installer_artifact_path() -> Path:
        """Get the path to the YXI Installer excutable."""
        curr_dir = Path(__file__).parent.parent.resolve()
        return curr_dir / "assets" / "executables" / "yxi-installer.pyz"

    def _get_yxi_paths(self) -> str:
        """Get the paths to the YXIs as a CLI string."""
        return " ".join([str(path) for path in self.yxi_paths])
