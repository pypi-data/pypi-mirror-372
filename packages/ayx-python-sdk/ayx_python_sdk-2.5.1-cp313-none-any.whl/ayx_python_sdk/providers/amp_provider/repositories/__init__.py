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
"""Repository classes that store information coming from the out of process manager."""
from typing import Iterable, Optional

from .dcm_repository import DCMRepository
from .environment_repository import EnvironmentRepository
from .grpc_repository import GrpcRepository
from .input_anchor_repository import InputAnchorRepository
from .input_connection_repository import InputConnectionRepository
from .input_metadata_repository import InputMetadataRepository
from .input_record_packet_repository import InputRecordPacketRepository
from .io_repository import IORepository
from .output_anchor_repository import OutputAnchorRepository
from .output_metadata_repository import OutputMetadataRepository
from .output_record_packet_repository import OutputRecordPacketRepository
from .plugin_class_repository import PluginClassRepository
from .singleton import Singleton
from .tool_config_repository import ToolConfigRepository


def clear_repositories(exclude: Optional[Iterable] = None) -> None:
    """Clear all repositories."""
    exclude = exclude or {}

    repos = [
        var()
        for name, var in globals().items()
        if "repository" in name.lower()
        and callable(var)
        and hasattr(var(), "clear_repository")
        and callable(var().clear_repository)
        and var() not in exclude
    ]

    for repo in repos:
        repo.clear_repository()


__all__ = [
    "DCMRepository",
    "EnvironmentRepository",
    "GrpcRepository",
    "InputAnchorRepository",
    "InputConnectionRepository",
    "InputMetadataRepository",
    "InputRecordPacketRepository",
    "IORepository",
    "OutputAnchorRepository",
    "OutputMetadataRepository",
    "OutputRecordPacketRepository",
    "PluginClassRepository",
    "Singleton",
    "ToolConfigRepository",
    "clear_repositories",
]
