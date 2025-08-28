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
"""Class that saves plugin class."""
from typing import Optional, Type

from ayx_python_sdk.core.plugin import Plugin
from ayx_python_sdk.providers.amp_provider.repositories.singleton import Singleton


class PluginClassRepository(metaclass=Singleton):
    """Repository that stores plugin class."""

    def __init__(self) -> None:
        """Initialize the plugin class repository."""
        self._plugin_class: Optional[Type[Plugin]] = None

    def save_plugin_class(self, plugin_class: Type[Plugin]) -> None:
        """
        Save plugin class.

        Parameters
        ----------
        plugin_class
            The custom Plugin class that's being used.
        """
        self._plugin_class = plugin_class

    def get_plugin_class(self) -> Type[Plugin]:
        """
        Get the plugin class.

        Returns
        -------
        Type[Plugin]
            The custom Plugin class that's being used.
        """
        if self._plugin_class is None:
            raise ValueError("Plugin class hasn't been saved.")

        return self._plugin_class

    def clear_repository(self) -> None:
        """Delete all data in the repository."""
        self._plugin_class = None
