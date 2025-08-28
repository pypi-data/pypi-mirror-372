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
"""Utility methods for AMP Provider classes."""
import logging
import os
import uuid
from pathlib import Path


from ayx_python_sdk.providers.amp_provider.utilities.constants import ToolEnvType

logger = logging.getLogger()


def tool_type() -> ToolEnvType:
    """Determine the Tool Environment Type based on TOOL_SERVICE_ADDRESS env var."""
    return (
        ToolEnvType.Service
        if "TOOL_SERVICE_ADDRESS" in os.environ
        else ToolEnvType.Desktop
    )


def get_temp_file(extension: str = "tmp", temp_dir: str = "./") -> "Path":
    """
    Create a temporary file managed by Designer.

    Parameters
    ----------
    extension
        The file extension of the temp file.
    temp_dir
        Directory in which to place the temp file.

    Returns
    -------
    Path
        The path to where the temp file is.
    """
    temp_file_name = f"temp-file-{str(uuid.uuid4())}.{str(extension)}"
    engine_temp_dir = temp_dir
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
