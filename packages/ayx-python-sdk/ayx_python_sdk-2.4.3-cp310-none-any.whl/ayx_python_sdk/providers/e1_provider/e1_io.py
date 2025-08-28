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
"""Proxy Class for SDK IO."""
from pathlib import Path
from typing import Any, cast

import AlteryxPythonSDK as Sdk

from ayx_python_sdk.core.doc_utilities import inherit_docs
from ayx_python_sdk.core.io_base import IoBase

import deprecation


@inherit_docs
class E1IO(IoBase):
    """Class that wraps all IO communication with Alteryx Designer."""

    __slots__ = ["_engine", "_tool_id"]

    def __init__(self, engine: Sdk.AlteryxEngine, tool_id: int) -> None:
        self._engine = engine
        self._tool_id = tool_id

    def error(self, error_msg: str) -> None:  # noqa: D102
        self._engine.output_message(
            self._tool_id, Sdk.EngineMessageType.error, str(error_msg)
        )

    def warn(self, warn_msg: str) -> None:  # noqa: D102
        self._engine.output_message(
            self._tool_id, Sdk.EngineMessageType.warning, str(warn_msg)
        )

    def info(self, info_msg: str) -> None:  # noqa: D102
        self._engine.output_message(
            self._tool_id, Sdk.EngineMessageType.info, str(info_msg)
        )

    def translate_msg(self, msg: str, *args: Any) -> str:  # noqa: D102
        stringified_args = [str(arg) for arg in args]
        translated_msg: str = self._engine.xmsg(msg, *stringified_args)
        return translated_msg

    def update_progress(self, percent: float) -> None:  # noqa: D102
        self._engine.output_tool_progress(self._tool_id, percent)

    def create_temp_file(
        self, extension: str = "tmp", options: int = 0
    ) -> Path:  # noqa: D102
        return Path(str(self._engine.create_temp_file_name(extension, options)))

    @deprecation.deprecated(
        deprecated_in="1.0.3",
        removed_in="2.0.0",
        details="Use functions of provider's dcm property instead",
    )  # type: ignore
    def decrypt_password(self, password: str) -> str:  # noqa: D102
        # mode 0 being passed here means decryption
        return cast(str, self._engine.decrypt_password(password, 0))
