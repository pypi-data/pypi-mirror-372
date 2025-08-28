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
"""Function definition for registering a plugin with the SDK."""
import sys
from typing import Literal, Optional, TYPE_CHECKING, Type

if TYPE_CHECKING:
    from ayx_python_sdk.core.plugin import Plugin  # noqa: F401
    from ayx_python_sdk.providers.e1_provider.e1_plugin_proxy import (  # noqa: F401
        E1PluginProxy,
    )

_ProviderTypes = Literal["e1", "e2", "file"]


def register_plugin(
    plugin_class: Type["Plugin"], version: Optional[str] = None
) -> Optional[Type["E1PluginProxy"]]:
    """
    Register a plugin with the SDK.

    The return value of this function should be assigned to a variable
    called AyxPlugin in the entrypoint to the tool in order for the
    E1 Python SDK to properly recognize it.

    Parameters
    ----------
    plugin_class
        Python Plugin to register. This plugin is written using the Python SDK.

    Returns
    -------
    E1PluginProxy, optional
        The Plugin, subclassed for the provider that it was registered with.

    """
    # TODO: Add v2 registration
    return {"e1": register_e1_plugin, "file": register_file_provider_plugin}[
        _get_provider()
    ](plugin_class, version)


def register_e1_plugin(
    user_plugin_class: Type["Plugin"], version: Optional[str] = None
) -> Type["E1PluginProxy"]:
    """
    Register a plugin with the E1 SDK Provider.

    Parameters
    ----------
    user_plugin_class
        Python Plugin to register.

    version
        Version of the tool being used.

    Returns
    -------
    E1PluginProxy
        Copy of the passed-in Plugin, subclassed for the E1 Provider.

    """
    # This makes a copy of the plugin proxy class. This is an unfortunate requirement
    # given the state of the existing python SDK since the environment shares an
    # interpreter. Without making a copy of the plugin proxy class on registration
    # the stateful property setting of user_plugin_class would be overwritten each
    # time a plugin loads and calls register_e1_plugin, since the library is only
    # loaded into memory once.
    from ayx_python_sdk.providers.e1_provider.e1_plugin_proxy import (  # noqa: F811
        E1PluginProxy,
    )

    class ProxyPluginCopy(E1PluginProxy):
        pass

    ProxyPluginCopy.user_plugin_class = user_plugin_class
    tool_directory_name = user_plugin_class.__name__

    if version:
        tool_directory_name = f"{tool_directory_name}_v{version}"
    ProxyPluginCopy.user_plugin_directory_name = tool_directory_name

    return ProxyPluginCopy


def register_file_provider_plugin(
    user_plugin_class: Type["Plugin"], version: Optional[str] = None
) -> None:
    """
    Register a plugin with the File Provider.

    Parameters
    ----------
    user_plugin_class
        Python Plugin to register.
    """
    import ayx_python_sdk.providers.file_provider.file_provider as ayx_file_provider

    ayx_file_provider.user_plugin_class = user_plugin_class
    return None


def _get_provider() -> _ProviderTypes:
    """
    Determine which provider is being used to run the Plugin.

    Returns
    -------
    _ProviderTypes
        A Literal that states which provider is being used: e1, e2 (AMP), or file.
    """
    if "AlteryxEngineCmd.exe" in sys.executable:
        return "e1"

    # For now, assume if it's not the e1 provider, then it's the file provider
    return "file"
