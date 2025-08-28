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
"""Class that saves input metadata information given the associated anchor name and connection name."""
import logging
from typing import Dict, TYPE_CHECKING

from ayx_python_sdk.providers.amp_provider.builders.metadata_builder import (
    MetadataBuilder,
)
from ayx_python_sdk.providers.amp_provider.repositories.singleton import Singleton

if TYPE_CHECKING:
    from ayx_python_sdk.core.metadata import Metadata as CoreMetadata
    from ayx_python_sdk.providers.amp_provider.resources.generated.metadata_pb2 import (
        Metadata as ProtobufMetadata,
    )

logger = logging.getLogger(__name__)


class InputMetadataRepository(metaclass=Singleton):
    """Repository that stores input metadata information."""

    _metadata_builder = MetadataBuilder()

    def __init__(self) -> None:
        """Initialize the input metadata repository."""
        self._metadata_map: Dict[str, Dict[str, "CoreMetadata"]] = {}

    def save_metadata(
        self, anchor_name: str, connection_name: str, metadata: "CoreMetadata"
    ) -> None:
        """
        Save input metadata information for the associated anchor name and connection name.

        Parameters
        ----------
        anchor_name
            The name of the input anchor that the metadata is associated with.
        connection_name
            The name of the input connection that the metadata is associated with.
        metadata
            The metadata information for the anchor and connection.
        """
        logger.debug(
            "Adding metadata to InputMetadataRepository for anchor %s/connection %s",
            anchor_name,
            connection_name,
        )
        self._metadata_map.setdefault(anchor_name, {})[connection_name] = metadata
        logger.debug("Current InputMetadataRepository State: %s", self._metadata_map)

    def save_grpc_metadata(
        self, anchor_name: str, connection_name: str, metadata: "ProtobufMetadata"
    ) -> None:
        """
        Save input metadata information for the associated anchor name and connection name given a Protobuf metadata message.

        Parameters
        ----------
        anchor_name
            The name of the input anchor that the metadata is associated with.
        connection_name
            The name of the input connection that the metadata is associated with.
        metadata
            The protobuf metadata information for the anchor and connection.
        """
        self.save_metadata(
            anchor_name, connection_name, self._metadata_builder.from_protobuf(metadata)
        )

    def get_metadata(
        self,
        anchor_name: str,
        connection_name: str,
    ) -> "CoreMetadata":
        """
        Get the input metadata associated with the given anchor name and connection name.

        Parameters
        ----------
        anchor_name
            The name of the input anchor that the metadata is associated with.
        connection_name
            The name of the input connection that the metadata is associated with.

        Returns
        -------
        CoreMetadata
            The metadata information for the anchor and connection.
        """
        if anchor_name not in self._metadata_map:
            raise ValueError(f"Anchor {anchor_name} not found in repository.")

        if connection_name not in self._metadata_map[anchor_name]:
            raise ValueError(
                f"Connection {connection_name} not found in repository for anchor {anchor_name}."
            )

        return self._metadata_map[anchor_name][connection_name]

    def delete_metadata(
        self,
        anchor_name: str,
        connection_name: str,
    ) -> None:
        """
        Delete the input metadata associated with the given anchor name and connection name.

        Parameters
        ----------
        anchor_name
            The name of the input anchor that the metadata is associated with.
        connection_name
            The name of the input connection that the metadata is associated with.
        """
        if anchor_name not in self._metadata_map:
            raise ValueError(f"Anchor {anchor_name} not found in repository.")

        if self._metadata_map[anchor_name].pop(connection_name, None) is None:
            raise ValueError(
                f"Connection {connection_name} not found in repository for anchor {anchor_name}."
            )
        logger.debug("Removing metadata for %s", anchor_name)
        if not self._metadata_map[anchor_name]:
            self._metadata_map.pop(anchor_name)
        logger.debug("Current InputMetadataRepository State: %s", self._metadata_map)

    def clear_repository(self) -> None:
        """Delete all data in the repository."""
        logger.debug("Clearing InputMetadataRepository")
        self._metadata_map = {}
        logger.debug("Current InputMetadataRepository State: %s", self._metadata_map)
