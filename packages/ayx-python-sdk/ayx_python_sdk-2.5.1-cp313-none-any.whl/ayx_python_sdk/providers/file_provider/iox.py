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
"""File Provider."""
from pathlib import Path
from typing import Any

from ayx_python_sdk.core.io_base import IoBase

import deprecation


class IO(IoBase):
    """Simple tool interface that will be used with Designer."""

    def __init__(self) -> None:
        """Instantiate the interface."""

    def error(self, error_msg: str) -> None:
        """Display an error in the Results window."""

    def warn(self, warn_msg: str) -> None:
        """Display a warning in the Results window."""

    def info(self, info_msg: str) -> None:
        """Display information in the Results window."""

    def translate_msg(self, msg: str, *args: Any) -> str:
        """Translate a message."""
        raise NotImplementedError()

    def update_progress(self, percent: float) -> None:
        """Update tool progress."""

    def create_temp_file(self, extension: str = "tmp", options: int = 0) -> Path:
        """Create a temporary file path."""
        return Path(extension)

    @deprecation.deprecated(
        deprecated_in="1.0.3",
        removed_in="2.0.0",
        details="Use functions of provider's dcm property instead",
    )  # type: ignore
    def decrypt_password(self, password: str) -> str:  # noqa: D102
        """Decrypt a password; will append '_decrypted' to the supplied password."""
        return password + "_decrypted"
