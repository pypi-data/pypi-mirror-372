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
Record Provider implementation.

Record providers instantiate input and output connections for the tool and pass
information along to the record processor.
"""
from abc import ABC, abstractmethod
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger
    from ayx_python_sdk.core.environment_base import EnvironmentBase
    from ayx_python_sdk.core.io_base import IoBase
    from ayx_python_sdk.core.input_anchor_base import InputAnchorBase
    from ayx_python_sdk.core.dcm import Dcm
    from ayx_python_sdk.core import OutputAnchorBase


class ProviderBase(ABC):
    """Record Provider for the tool."""

    @property
    @abstractmethod
    def tool_config(self) -> Dict:
        """Get Config XML from this provider."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def logger(self) -> "Logger":
        """
        Get the Logger for the provider.

        Returns
        -------
        Logger
            Python logging object.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def io(self) -> "IoBase":
        """
        Get the IO (input/output) object from this provider.

        Returns
        -------
        IoBase
            An instance of a concrete IO object.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def environment(self) -> "EnvironmentBase":
        """
        Get the Environment object from this provider.

        Returns
        -------
        EnvironmentBase
            An instance of a concrete Environment object.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_input_anchor(self, name: str) -> "InputAnchorBase":
        """
        Get an input anchor by name.

        Parameters
        ----------
        name
            The name of the anchor to get.

        Returns
        -------
        InputAnchorBase
            An instance of a concrete InputAnchorBase object with the name requested.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_output_anchor(self, name: str) -> "OutputAnchorBase":
        """
        Get an output anchor by name.

        Parameters
        ----------
        name
            The name of the anchor to get.

        Returns
        -------
        OutputAnchorBase
            An instance of a concrete OutputAnchorBase object with the name requested.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def dcm(self) -> "Dcm":
        """
        Get the DCM object from this provider.

        Returns
        -------
        Dcm
            An instance of a concrete Dcm object.
        """
        raise NotImplementedError()
