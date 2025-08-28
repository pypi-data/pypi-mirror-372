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
"""Class that saves and retrieves AMP IO information."""
import logging
import uuid
from pathlib import Path
from typing import Any, cast

from ayx_python_sdk.core.exceptions import WorkflowRuntimeError
from ayx_python_sdk.providers.amp_provider.repositories import EnvironmentRepository
from ayx_python_sdk.providers.amp_provider.repositories import GrpcRepository
from ayx_python_sdk.providers.amp_provider.repositories.singleton import Singleton
from ayx_python_sdk.providers.amp_provider.resources.generated.output_message_data_pb2 import (
    OutputMessageData,
    OutputMessageTypes,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.password_data_pb2 import (
    PasswordData,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.translate_message_data_pb2 import (
    TranslateMessageData,
)

logger = logging.getLogger(__name__)


class IORepository(metaclass=Singleton):
    """Repository that stores IO information."""

    def __init__(self) -> None:
        """Initialize the IO repository."""

    @staticmethod
    def save_error(error_msg: str) -> None:
        """
        Display an error message in the Results window.

        Parameters
        ----------
        error_msg
            The error message to be output.
        """
        GrpcRepository().get_sdk_engine_client().OutputMessage(
            OutputMessageData(
                message_type=OutputMessageTypes.OMT_Error, message=error_msg
            )
        )

    @staticmethod
    def save_warn(warn_msg: str) -> None:
        """
        Display a warning message in the Results window.

        Parameters
        ----------
        warn_msg
            The warning message to be output.
        """
        GrpcRepository().get_sdk_engine_client().OutputMessage(
            OutputMessageData(
                message_type=OutputMessageTypes.OMT_Warning, message=warn_msg
            )
        )

    @staticmethod
    def save_info(info_msg: str) -> None:
        """
        Display an info message in the Results window.

        Parameters
        ----------
        info_msg
            The info message to be output.
        """
        GrpcRepository().get_sdk_engine_client().OutputMessage(
            OutputMessageData(
                message_type=OutputMessageTypes.OMT_Info, message=info_msg
            )
        )

    @staticmethod
    def get_translate_msg(msg: str, *args: Any) -> str:
        """
        Translate a message to the current locale.

        Parameters
        ----------
        msg
            Message to translate.
        *args
            Interpolation data for the string.

        Returns
        -------
        str
            The message, translated into the locale.
        """
        interpolation_data = [str(arg) for arg in args] if len(args) > 0 else []
        res = (
            GrpcRepository()
            .get_sdk_engine_client()
            .TranslateMessage(
                TranslateMessageData(
                    unlocalized_string=msg, interpolation_data=interpolation_data
                )
            )
        )

        return cast(str, res.translated_message)

    @staticmethod
    def update_progress(percent: float) -> None:
        """
        Update tool progress.

        Parameters
        ----------
        percent
            The progress (how close the connection is to processing all records) as a percentage.
        """
        # TODO

    @staticmethod
    def get_temp_file(extension: str = "tmp") -> "Path":
        """
        Create a temporary file managed by Designer.

        Parameters
        ----------
        extension
            The file extension of the temp file.

        Returns
        -------
        Path
            The path to where the temp file is.
        """
        temp_file_name = f"temp-file-{str(uuid.uuid4())}.{str(extension)}"
        engine_temp_dir = EnvironmentRepository().get_temp_dir()
        temp_file_path = Path(engine_temp_dir) / (temp_file_name)
        try:
            temp_file_path.touch()
        except FileNotFoundError:
            # path does not exist
            logger.error("Engine.TempFilePath (%s) does not exist", engine_temp_dir)
        except IOError:
            # path exists but no write permissions
            logger.error("No write permissions for directory %s", engine_temp_dir)

        return Path(temp_file_path)

    @staticmethod
    def decrypt_password(password: str) -> str:  # noqa: D102
        """
        Decrypt password.

        Parameters
        ----------
        password
            The password to decrypt.

        Returns
        -------
        str
            The decrypted password.
        """
        import grpc

        try:
            decrypted = (
                GrpcRepository()
                .get_sdk_engine_client()
                .DecryptPassword(PasswordData(password=password))
            )
        except grpc.RpcError:
            raise WorkflowRuntimeError("Error decrypting password")
        return cast(str, decrypted.password)
