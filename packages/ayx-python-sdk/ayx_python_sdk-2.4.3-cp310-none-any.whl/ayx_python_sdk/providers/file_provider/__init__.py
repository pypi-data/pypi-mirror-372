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
"""Alteryx Python SDK - File Adapter for standalone testing."""

from .file_adapter import FileAdapter
from .file_provider import FileProvider
from .file_provider_input_anchor import FileProviderInputAnchor
from .file_provider_input_connection import FileProviderInputConnection
from .file_provider_output_anchor import FileProviderOutputAnchor
from .tool_input import AnchorDefinition, ToolDefinition, ToolInput

__all__ = [
    "AnchorDefinition",
    "FileAdapter",
    "FileProvider",
    "FileProviderInputAnchor",
    "FileProviderInputConnection",
    "FileProviderOutputAnchor",
    "ToolDefinition",
    "ToolInput",
]
