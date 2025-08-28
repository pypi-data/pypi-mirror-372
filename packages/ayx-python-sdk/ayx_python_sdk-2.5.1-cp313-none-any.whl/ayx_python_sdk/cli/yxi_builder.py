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
"""Class for building YXIs."""
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path


class YxiBuilder:
    """YXI Builder class."""

    def __init__(
        self,
        workspace_dir: Path,
        output_yxi_path: Path,
        requirements_tool: str,
        package_requirements: bool = True,
    ) -> None:
        """Construct a YXI Builder."""
        self._workspace_dir = workspace_dir
        self._output_yxi_path = output_yxi_path
        self._requirements_tool = requirements_tool
        self._package_requirements = package_requirements

    def build_yxi(self) -> None:
        """Build the YXI."""
        zip_path = Path(f"{uuid.uuid4()}.zip")

        with tempfile.TemporaryDirectory() as yxi_temp_folder:
            yxi_temp_path = Path(yxi_temp_folder) / "temp"
            self._copy_workspace(yxi_temp_path)

            if self._package_requirements:
                self._handle_requirements(yxi_temp_path)

            self._delete_pycache_directories(yxi_temp_path)

            shutil.make_archive(zip_path.stem, "zip", str(yxi_temp_path))

        shutil.move(str(zip_path), str(self._output_yxi_path))

    def _copy_workspace(self, dest_dir: Path) -> None:
        shutil.copytree(str(self._workspace_dir), str(dest_dir))

    def _handle_requirements(self, temp_yxi_dir: Path) -> None:
        workspace_requirements_path = self._workspace_dir / "requirements.txt"
        temp_tools_requirements_path = (
            temp_yxi_dir / self._requirements_tool / "requirements.txt"
        )

        # Copy requirements to requirements tool
        shutil.copy(str(workspace_requirements_path), str(temp_tools_requirements_path))

        # E1 Provider ships wheels inside of a tool, so we must link to them in the
        # requirements.txt so that the pip install finds the wheels offline
        self._add_link_wheels_to_requirements(temp_tools_requirements_path)

        # Download wheels to the requirements tool wheels directory
        self._download_pip_packages(
            temp_yxi_dir / self._requirements_tool / "wheels",
            workspace_requirements_path,
        )

    def _add_link_wheels_to_requirements(self, requirements_path: Path) -> None:
        user_install_wheels = f'--find-links "${{APPDATA}}/Alteryx/Tools/{self._requirements_tool}/wheels"\n'
        admin_install_wheels = f'--find-links "${{ALLUSERSPROFILE}}/Alteryx/Tools/{self._requirements_tool}/wheels"\n'

        with requirements_path.open(mode="r") as requirements_file:
            requirements = requirements_file.readlines()

        full_requirements_list = [
            user_install_wheels,
            admin_install_wheels,
        ] + requirements

        with requirements_path.open(mode="w") as requirements_file:
            requirements_file.writelines(full_requirements_list)

    @staticmethod
    def _download_pip_packages(dest_dir: Path, requirements_path: Path) -> None:
        """Download the pip wheels and store in dest_dir."""
        dest_dir.mkdir()

        commands = [
            sys.executable,
            "-m",
            "pip",
            "download",
            "--platform",
            "win_amd64",
            "--no-deps",
            "-r",
            f"{requirements_path}",
            "-d",
            f"{dest_dir}",
        ]

        subprocess.run(commands)

    @staticmethod
    def _delete_pycache_directories(root_dir: Path) -> None:
        """Delete all the pycache subdirectories of a given root."""
        pycache_dirs = [
            Path(root) / directory
            for root, directories, _ in os.walk(str(root_dir))
            for directory in directories
            if directory == "__pycache__"
        ]
        for directory in pycache_dirs:
            shutil.rmtree(str(directory), ignore_errors=True)
