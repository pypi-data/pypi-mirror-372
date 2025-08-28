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
"""AMP Provider: Proxy class for SDK IO (input/output)."""
from pathlib import Path
from typing import Any

from ayx_python_sdk.core import IoBase
from ayx_python_sdk.core.doc_utilities import inherit_docs
from ayx_python_sdk.providers.amp_provider.repositories import IORepository

import deprecation


@inherit_docs
class AMPIO(IoBase):
    """Class that wraps all IO with Designer."""

    def error(self, error_msg: str) -> None:  # noqa: D102
        IORepository().save_error(error_msg)

    def warn(self, warn_msg: str) -> None:  # noqa: D102
        IORepository().save_warn(warn_msg)

    def info(self, info_msg: str) -> None:  # noqa: D102
        IORepository().save_info(info_msg)

    def translate_msg(self, msg: str, *args: Any) -> str:  # noqa: D102
        return IORepository().get_translate_msg(msg, *args)

    def update_progress(self, percent: float) -> None:  # noqa: D102
        IORepository().update_progress(percent)

    def create_temp_file(
        self, extension: str = "tmp", options: int = 0
    ) -> "Path":  # noqa: D102
        """
        Create a temporary file managed by Designer.

        .. deprecated:: AMP
            `options` is not used in AMP because there is no longer a
            differentiation between temporary persistent and temporary non-persitent
            files.

        """
        return IORepository().get_temp_file(extension)

    @deprecation.deprecated(
        deprecated_in="1.0.3",
        removed_in="2.0.0",
        details="Use functions of provider's dcm property instead",
    )  # type: ignore
    def decrypt_password(self, password: str) -> str:  # noqa: D102
        return IORepository().decrypt_password(password)
