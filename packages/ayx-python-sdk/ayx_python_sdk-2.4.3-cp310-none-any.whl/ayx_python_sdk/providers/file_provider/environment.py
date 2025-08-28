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
"""File provider runtime environment information."""
import os
from pathlib import Path
from typing import Optional

from ayx_python_sdk.core.doc_utilities import inherit_docs
from ayx_python_sdk.core.environment_base import (
    EnvironmentBase,
    Locale,
    UpdateMode,
)

import xmltodict


@inherit_docs
class Environment(EnvironmentBase):
    """Environment information for the file provider."""

    def __init__(self, update_config_path: Optional[Path] = None) -> None:
        """
        Instantiate the file provider environment information.

        Parameters
        ----------
        update_config_path
            The path to use if the tool config file should be updated.
        """
        self.__update_config_path = update_config_path

    @property
    def update_only(self) -> bool:
        """
        Check if the file provider is running in update-only mode.

        Returns
        -------
        bool
            False in the file provider because update-only mode is not implemented.
        """
        # TODO change this when update only mode gets implemented
        return False

    @property
    def update_mode(self) -> UpdateMode:
        """
        Return NO_UPDATE_MODE because update-only mode is not implemented in the file provider.

        Returns
        -------
        UpdateMode
            Returns NO_UPDATE_MODE.
        """
        # TODO change this when update only mode gets implemented
        return UpdateMode.NO_UPDATE_MODE

    @property
    def designer_version(self) -> str:
        """
        Return 0.0.0.0 because Designer is not being used.

        Returns
        -------
        str
            0.0.0.0
        """
        return "0.0.0.0"

    @property
    def workflow_dir(self) -> Path:  # noqa: D102
        return Path(os.getcwd())

    @property
    def workflow_id(self) -> str:  # noqa: D102
        return ""

    def parse_settings_key_value(
        self, settings_str: str, line_delimiter: str = "\n", key_delimiter: str = "="
    ) -> dict:  # noqa: D102
        return super().parse_settings_key_value(
            settings_str, line_delimiter=line_delimiter, key_delimiter=key_delimiter
        )

    def get_settings_conf(
        self, keys: list, version_override: str = ""
    ) -> dict:  # noqa: D102
        """Parse xml to retrieve settings for a given designer version."""
        return super().get_settings_conf(keys, version_override)

    @property
    def proxy_configuration(self) -> dict:  # noqa: D102
        """Retrieve proxy config from UserSettings.xml."""
        keys = ["AlteryxSettings", "GloablSettings", "ProxyConfiguration"]
        return self.get_settings_conf(keys)

    @property
    def alteryx_install_dir(self) -> Path:
        """File provider does not use Designer, so this should raise NotImplementedError."""
        raise NotImplementedError()

    @property
    def alteryx_locale(self) -> Locale:
        """File provider does not use Designer, so automatically return English."""
        return "en"

    @property
    def tool_id(self) -> int:  # noqa: D102
        return -1

    def update_tool_config(self, new_config: dict) -> None:  # noqa: D102
        if self.__update_config_path:
            xml = xmltodict.unparse(
                input_dict={"Configuration": new_config},
                pretty=True,
                short_empty_elements=True,
            )
            with open(self.__update_config_path, "w") as fd:
                fd.write(xml + "\n")
