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
"""Class that saves output metadata information given the associated anchor name."""
import logging
from typing import Dict, TYPE_CHECKING

from ayx_python_sdk.providers.amp_provider.builders.metadata_builder import (
    MetadataBuilder,
)
from ayx_python_sdk.providers.amp_provider.repositories import GrpcRepository
from ayx_python_sdk.providers.amp_provider.repositories.singleton import Singleton
from ayx_python_sdk.providers.amp_provider.resources.generated.outgoing_metadata_push_pb2 import (
    OutgoingMetadataPush,
)

if TYPE_CHECKING:
    from ayx_python_sdk.core.metadata import Metadata as CoreMetadata
    from ayx_python_sdk.providers.amp_provider.resources.generated.metadata_pb2 import (
        Metadata as ProtobufMetadata,
    )


logger = logging.getLogger(__name__)


class OutputMetadataRepository(metaclass=Singleton):
    """Repository that stores output metadata information."""

    _metadata_builder = MetadataBuilder()

    def __init__(self) -> None:
        """Initialize the output metadata repository."""
        self._metadata_map: Dict[str, "CoreMetadata"] = {}

    def save_metadata(self, anchor_name: str, metadata: "CoreMetadata") -> None:
        """
        Save output metadata information for the associated anchor name.

        Parameters
        ----------
        anchor_name
            The name of the anchor.
        metadata
            The metadata of the record packets that will be associated with this anchor.
        """
        logger.debug("Saving metadata %s to anchor %s", metadata, anchor_name)
        self._metadata_map[anchor_name] = metadata
        logger.debug("Current OutputMetadataRepository State: %s", self._metadata_map)

        try:
            client = GrpcRepository().get_sdk_engine_client()
        except ValueError:
            pass
        else:
            client.PushOutgoingMetadata(
                OutgoingMetadataPush(
                    output_anchor_name=anchor_name,
                    metadata=self.get_grpc_metadata(anchor_name),
                )
            )

    def get_metadata(self, anchor_name: str) -> "CoreMetadata":
        """
        Get the output metadata associated with the given anchor name.

        Parameters
        ----------
        anchor_name
            The name of the anchor.

        Returns
        -------
        CoreMetadata
            Retrieves the metadata that is associatd with the specified anchor.
        """
        if anchor_name not in self._metadata_map:
            raise ValueError(f"Anchor {anchor_name} not found in repository.")

        return self._metadata_map[anchor_name]

    def get_grpc_metadata(self, anchor_name: str) -> "ProtobufMetadata":
        """
        Get the output Protobuf metadata message associated with the given anchor name.

        Parameters
        ----------
        anchor_name
            The name of the anchor.

        Returns
        -------
        ProtobufMetadata
            The metadata of the record packets that will be associated with this anchor as a protobuf object.
        """
        metadata = self.get_metadata(anchor_name)

        return self._metadata_builder.to_protobuf(metadata)

    def delete_metadata(self, anchor_name: str) -> None:
        """
        Delete the output metadata associated with the given anchor name.

        Parameters
        ----------
        anchor_name
            The name of the anchor to delete.
        """
        if anchor_name not in self._metadata_map:
            raise ValueError(f"Anchor {anchor_name} not found in repository.")
        logger.debug("Removing metadata associated with anchor %s", anchor_name)
        self._metadata_map.pop(anchor_name)
        logger.debug("Current OutputAnchorRepository State: %s", self._metadata_map)

    def clear_repository(self) -> None:
        """Delete all data in the repository."""
        logger.debug("Clearing OutputAnchorRepository")
        self._metadata_map = {}
        logger.debug("Current OutputAnchorRepository State: %s", self._metadata_map)
