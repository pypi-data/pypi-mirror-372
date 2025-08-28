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
"""
The Abstract Base class definition for plugins.

For a custom plugin, a user will inherit from Plugin and implement
all of the abstract methods.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ayx_python_sdk.core.input_connection_base import InputConnectionBase
    from ayx_python_sdk.core.provider_base import ProviderBase


class Plugin(ABC):
    """The Abstract Base class for Plugin."""

    @abstractmethod
    def __init__(self, provider: "ProviderBase"):
        """
        Initialize the plugin from the provider.

        This method IS called during update-only mode.

        Parameters
        ----------
        provider
            The provider object that provides resources for reading and writing data.

        config
            A dictionary that contains the tool configuration.
        """
        raise NotImplementedError()

    @abstractmethod
    def on_input_connection_opened(
        self, input_connection: "InputConnectionBase"
    ) -> None:
        """
        Process an opened input connection.

        The method that gets called whenever an input connection is opened.

        When an input connection is opened, it receives metadata. Prior to being
        opened, its metadata is None.

        This method IS called during update-only mode.

        In this method, a Plugin designer should make sure to open any output anchors
        during update-only mode in order to ensure that metadata is properly propagated
        in Designer.

        Parameters
        ----------
        input_connection
            The input connection that was opened.
        """
        raise NotImplementedError()

    @abstractmethod
    def on_record_packet(self, input_connection: "InputConnectionBase") -> None:
        """
        Process any incoming records.

        The method that gets called whenever an input connection receives records.

        This method IS NOT called during update-only mode.

        In this method, a Plugin designer should read from the input connection
        and process the record packet that it produces.

        Parameters
        ----------
        input_connection
            The input connection that received a record.
        """
        raise NotImplementedError()

    @abstractmethod
    def on_complete(self) -> None:
        """
        Clean up any plugin resources, or push records for an input tool.

        This method gets called when all other plugin processing is complete.

        This method IS NOT called during update-only mode.

        In this method, a Plugin designer should perform any cleanup for their plugin.
        However, if the plugin is an input-type tool (it has no incoming connections),
        processing (record generation) should occur here.

        Note: A tool with an optional input anchor and no incoming connections should
        also write any records to output anchors here.
        """
        raise NotImplementedError()
