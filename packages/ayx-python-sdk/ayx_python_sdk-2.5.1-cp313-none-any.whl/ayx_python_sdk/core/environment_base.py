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
"""Runtime Environment information."""
import os
from abc import ABC, abstractmethod
from enum import Enum, unique
from pathlib import Path
from typing import Literal

import xmltodict

Locale = Literal["en", "it", "fr", "de", "ja", "es", "pt", "zh"]


@unique
class UpdateMode(Enum):
    """The types of update modes that can run in Alteryx Designer."""

    NO_UPDATE_MODE = ""
    QUICK = "Quick"
    FULL = "Full"


class EnvironmentBase(ABC):
    """
    Environment Information class definition.

    This class provides information about the runtime environment
    of the tool that is running. For example, if it is running as update
    only, the version of the system running, etc.
    """

    @property
    @abstractmethod
    def update_only(self) -> bool:
        """
        Check if the engine is running in update-only mode.

        Returns
        -------
        bool
            Boolean value that indicates if the engine is running in update only.

        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def update_mode(self) -> UpdateMode:
        """
        Get the type of update running.

        Returns
        -------
        UpdateMode
            Enumeration corresponding to the update mode that the workflow is running in.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def designer_version(self) -> str:
        """
        Return the version of Designer that is being used.

        Returns
        -------
        str
            A version in the format of 1.2.3.4

        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def workflow_dir(self) -> Path:
        """
        Get the directory for the currently-running workflow.

        Returns
        -------
        Path
            The workflow directory as a Path object.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def workflow_id(self) -> str:
        """
        Get the WorkflowRunGuid for the currently-running workflow.

        Returns
        -------
        str
            The workflow id.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def alteryx_install_dir(self) -> Path:
        """
        Get the Alteryx install directory.

        Returns
        -------
        Path
            The Alteryx install directory as a Path object.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def alteryx_locale(self) -> Locale:
        """
        Retrieve the locale code from Alteryx Designer User Settings.

        Returns
        -------
        Locale
            The language/region that Alteryx is using to display messages.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def tool_id(self) -> int:
        """
        Get the current tool's workflow ID.

        Returns
        -------
        int
            Tool's ID (specified by developer).
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def proxy_configuration(self) -> dict:
        """
        Get the proxy configuration settings if they exist.

        Returns
        -------
        dict
            Proxy Configuration as set in Designer
        """
        raise NotImplementedError()

    @abstractmethod
    def get_settings_conf(
        self, keys: list, version_override: str = ""
    ) -> dict:  # noqa: D102
        """Parse xml to retrieve settings."""
        designer_version = (
            self.designer_version[0:6] if not version_override else version_override
        )
        user_settings_path = (
            Path(os.environ["APPDATA"])
            / "Alteryx"
            / "Engine"
            / designer_version
            / "UserSettings.xml"
        )
        with open(user_settings_path) as f:
            user_settings = xmltodict.parse(f.read())
            while keys:
                user_settings = user_settings[keys[0]]
                keys = keys[1:]
        return user_settings

    @abstractmethod
    def parse_settings_key_value(
        self, settings_str: str, line_delimiter: str = "\n", key_delimiter: str = "="
    ) -> dict:  # noqa: D102
        """Extract a key value pair from an xml text entry set by Designer."""
        parsed_values = {}
        for key_val_pair in settings_str.split(line_delimiter):
            keyval = key_val_pair.split(key_delimiter, 1)
            # might have a blank or unset key
            if len(keyval) > 1:
                parsed_values[keyval[0]] = keyval[1]
        return parsed_values

    @abstractmethod
    def update_tool_config(self, new_config: dict) -> None:
        """
        Update the tool's configuration.

        Parameters
        ----------
        new_config
            The new configuration to set for the tool.

        Returns
        -------
        None

        """
        raise NotImplementedError()
