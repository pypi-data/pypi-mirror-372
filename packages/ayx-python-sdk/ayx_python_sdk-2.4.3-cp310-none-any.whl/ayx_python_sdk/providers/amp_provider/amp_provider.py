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
"""AMP Provider: SDK Provider class definition."""
from logging import Logger, getLogger
from typing import Dict, TYPE_CHECKING

from ayx_python_sdk.core import ProviderBase
from ayx_python_sdk.core.doc_utilities import inherit_docs
from ayx_python_sdk.providers.amp_provider import AMPEnvironment
from ayx_python_sdk.providers.amp_provider.amp_dcm import AMPDCM
from ayx_python_sdk.providers.amp_provider.amp_io import AMPIO
from ayx_python_sdk.providers.amp_provider.repositories import InputAnchorRepository
from ayx_python_sdk.providers.amp_provider.repositories import OutputAnchorRepository
from ayx_python_sdk.providers.amp_provider.repositories import ToolConfigRepository

if TYPE_CHECKING:
    from ayx_python_sdk.providers.amp_provider.amp_input_anchor import AMPInputAnchor
    from ayx_python_sdk.providers.amp_provider.amp_output_anchor import AMPOutputAnchor
    from ayx_python_sdk.providers.amp_provider.amp_driver import AMPDriver


@inherit_docs
class AMPProvider(ProviderBase):
    """Class that provides resources to plugins that are run with the AMP Provider."""

    def __init__(self) -> None:
        """Initialize the AMP resource provider."""
        self.__environment: "AMPEnvironment" = AMPEnvironment()
        self.__io: "AMPIO" = AMPIO()
        self.__dcm: "AMPDCM" = AMPDCM()
        self._driver: "AMPDriver" = None

    @property
    def logger(self) -> "Logger":  # noqa: D102
        return getLogger()

    @property
    def io(self) -> "AMPIO":  # noqa: D102
        return self.__io

    @property
    def dcm(self) -> "AMPDCM":  # noqa: D102
        return self.__dcm

    @property
    def environment(self) -> "AMPEnvironment":  # noqa: D102
        return self.__environment

    def get_input_anchor(self, name: str) -> "AMPInputAnchor":  # noqa: D102
        return InputAnchorRepository().get_anchor(name)

    def get_output_anchor(self, name: str) -> "AMPOutputAnchor":  # noqa: D102
        return OutputAnchorRepository().get_anchor(name)

    @property
    def tool_config(self) -> Dict:  # noqa: D102
        return ToolConfigRepository().get_tool_config()
