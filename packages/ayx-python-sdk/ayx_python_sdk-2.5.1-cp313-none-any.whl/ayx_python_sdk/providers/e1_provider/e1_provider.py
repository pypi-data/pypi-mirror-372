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
"""E1 SDK Provider Class."""
from logging import Logger
from typing import Any, TYPE_CHECKING

from ayx_python_sdk.core.doc_utilities import inherit_docs
from ayx_python_sdk.core.provider_base import ProviderBase
from ayx_python_sdk.providers.e1_provider import E1InputAnchor
from ayx_python_sdk.providers.e1_provider.e1_output_anchor import E1OutputAnchor

if TYPE_CHECKING:
    from ayx_python_sdk.providers.e1_provider.workflow_config import (
        WorkflowConfiguration,
    )
    from ayx_python_sdk.providers.e1_provider.e1_environment import E1Environment
    from ayx_python_sdk.providers.e1_provider.e1_plugin_proxy import E1PluginProxy
    from ayx_python_sdk.providers.e1_provider.e1_io import E1IO
    from ayx_python_sdk.providers.e1_provider.e1_dcm import E1DCM


@inherit_docs
class E1Provider(ProviderBase):
    """Provides resources generated from the E1 Python SDK."""

    def __init__(
        self, plugin_proxy: "E1PluginProxy", workflow_config: "WorkflowConfiguration"
    ):
        """Construct the E1Provider."""
        self._plugin_proxy = plugin_proxy
        self._workflow_config = workflow_config

    @property
    def tool_config(self) -> Any:
        """Get config XML."""
        return self._workflow_config.data

    @property
    def logger(self) -> Logger:  # noqa: D102
        return self._plugin_proxy.logger

    @property
    def io(self) -> "E1IO":  # noqa: D102
        return self._plugin_proxy.io

    @property
    def dcm(self) -> "E1DCM":  # noqa: D102
        return self._plugin_proxy.dcm

    @property
    def environment(self) -> "E1Environment":  # noqa: D102
        return self._plugin_proxy.environment

    def get_input_anchor(self, name: str) -> E1InputAnchor:  # noqa: D102
        return E1InputAnchor(self._plugin_proxy.get_input_anchor(name))

    def get_output_anchor(self, name: str) -> E1OutputAnchor:  # noqa: D102
        return E1OutputAnchor(
            self._plugin_proxy.get_output_anchor(name), self._plugin_proxy.engine
        )
