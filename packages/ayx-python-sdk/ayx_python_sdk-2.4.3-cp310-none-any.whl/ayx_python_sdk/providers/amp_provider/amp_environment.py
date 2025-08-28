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
"""Proxy Class for managing the SDK environment on Alteryx Multi-threaded Processing (AMP)."""
from typing import TYPE_CHECKING

from ayx_python_sdk.core.doc_utilities import inherit_docs
from ayx_python_sdk.core.environment_base import EnvironmentBase
from ayx_python_sdk.providers.amp_provider.repositories import EnvironmentRepository

if TYPE_CHECKING:
    from ayx_python_sdk.core.environment_base import UpdateMode, Locale
    from pathlib import Path


@inherit_docs
class AMPEnvironment(EnvironmentBase):
    """Variables that describe the Designer environment when AMP is enabled."""

    @property
    def update_only(self) -> bool:  # noqa: D102
        return EnvironmentRepository().get_update_only()

    @property
    def update_mode(self) -> "UpdateMode":  # noqa: D102
        return EnvironmentRepository().get_update_mode()

    @property
    def designer_version(self) -> str:  # noqa: D102
        return EnvironmentRepository().get_designer_version()

    @property
    def workflow_dir(self) -> "Path":  # noqa: D102
        return EnvironmentRepository().get_workflow_dir()

    @property
    def alteryx_install_dir(self) -> "Path":  # noqa: D102
        return EnvironmentRepository().get_alteryx_install_dir()

    @property
    def alteryx_locale(self) -> "Locale":  # noqa: D102
        return EnvironmentRepository().get_alteryx_locale()

    @property
    def tool_id(self) -> int:  # noqa: D102
        return EnvironmentRepository().get_tool_id()

    @property
    def proxy_configuration(self) -> dict:  # noqa: D102
        return EnvironmentRepository().get_proxy_configuration()

    def parse_settings_key_value(
        self, settings_str: str, line_delimiter: str = "\n", key_delimiter: str = "="
    ) -> dict:  # noqa: D102
        return super().parse_settings_key_value(
            settings_str, line_delimiter=line_delimiter, key_delimiter=key_delimiter
        )

    def get_settings_conf(self, *args: list) -> dict:  # noqa: D102
        return super().get_settings_conf(*args)

    def update_tool_config(self, new_config: dict) -> None:  # noqa: D102
        EnvironmentRepository().save_tool_config(new_config)
