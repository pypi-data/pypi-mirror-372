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
"""Plugin class loader logic."""
import importlib
from typing import Type, cast

from ayx_python_sdk.core.plugin import Plugin
from ayx_python_sdk.core.plugin_v2 import PluginV2


class PluginNotFoundError(Exception):
    """Plugin not found exception."""

    pass


class PluginClassError(Exception):
    """Plugin class error."""

    pass


def load_plugin_class(plugins_package: str, tool_name: str) -> Type[Plugin]:
    """
    Dynamically load the plugin class.

    Parameters
    ----------
    plugins_package: str
        Path to the plugins to load from.

    tool_name: str
        Name of the tool to load.

    Returns
    -------
    plugin_class: Type[Plugin]

    Raises
    ------
    ModuleNotFoundError
        If module couldn't be found

    PluginNotFoundError
        If the module doesn't contain the specified tool

    PluginClassError
        If the specified tool isn't a Plugin.
    """
    try:
        plugins_module = importlib.import_module(plugins_package)
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            f"ERROR: Couldn't find module {plugins_package} for loading plugins."
        )
    try:
        plugin_class = getattr(plugins_module, tool_name)
    except AttributeError:
        raise PluginNotFoundError(
            f"ERROR: Plugin module {plugins_package} doesn't contain a tool named {tool_name}."
        )
    if not (issubclass(plugin_class, Plugin) or issubclass(plugin_class, PluginV2)):
        raise PluginClassError(
            f"ERROR: {tool_name} class from {plugins_package} module is not a Plugin."
        )
    return cast(Type[Plugin], plugin_class)
