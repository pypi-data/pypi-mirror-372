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

from ayx_python_sdk.core import Anchor

if TYPE_CHECKING:
    from ayx_python_sdk.providers.amp_provider.amp_provider_v2 import AMPProviderV2

    from pyarrow import Table


class PluginV2(ABC):
    """The Abstract Base class for Plugin."""

    @abstractmethod
    def __init__(self, provider: "AMPProviderV2"):
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
    def on_incoming_connection_complete(self, anchor: Anchor) -> None:
        """
        Call when an incoming connection is done sending data including when no data is sent on an optional input anchor.

        This method IS NOT called during update-only mode.

        Parameters
        ----------
        anchor
            NamedTuple containing anchor.name and anchor.connection_name.
        """
        raise NotImplementedError()

    @abstractmethod
    def on_record_batch(self, batch: "Table", anchor: Anchor) -> None:
        """
        Process the passed record batch.

        The method that gets called whenever the plugin receives a record batch on an input.

        This method IS NOT called during update-only mode.

        Parameters
        ----------
        batches
            A pyarrow Table containing the received batch.
        anchor
            A namedtuple('Anchor', ['name', 'connection_name']) containing input connection identifiers.
        """
        raise NotImplementedError()

    @abstractmethod
    def on_complete(self) -> None:
        """
        Clean up any plugin resources, or push records for an input tool.

        This method gets called when all other plugin processing is complete.

        In this method, a Plugin designer should perform any cleanup for their plugin.
        However, if the plugin is an input-type tool (it has no incoming connections),
        processing (record generation) should occur here.

        Note: A tool with an optional input anchor and no incoming connections should
        also write any records to output anchors here.
        """
        raise NotImplementedError()
