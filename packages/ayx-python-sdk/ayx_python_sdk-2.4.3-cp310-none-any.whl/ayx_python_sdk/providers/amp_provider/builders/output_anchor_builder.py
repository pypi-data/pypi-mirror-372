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
"""Builder file for Output Anchor."""
import logging
import sys
from typing import TYPE_CHECKING

from ayx_python_sdk.providers.amp_provider.builders.metadata_builder import (
    MetadataBuilder,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.outgoing_anchor_pb2 import (
    OutgoingAnchor as ProtobufOutputAnchor,
)

if TYPE_CHECKING:
    from ayx_python_sdk.providers import AMPOutputAnchor


logger = logging.getLogger(__name__)


class OutputAnchorBuilder:
    """Builder class for serializing and deserializing output anchors."""

    @staticmethod
    def from_protobuf(
        protobuf_output_anchor: ProtobufOutputAnchor,
    ) -> "AMPOutputAnchor":
        """
        Given an AMPOutputAnchor as a protobuf, return its Python object.

        Parameters
        ----------
        protobuf_output_anchor
            Protobuf object to be serialized into an AMP metadata.

        Returns
        -------
        AMPOutputAnchor
            The AMP Metadata representation of the protobuf object.
        """
        from ayx_python_sdk.providers.amp_provider.amp_output_anchor import (
            AMPOutputAnchor,
        )

        logger.debug(
            "Deserializing Output Anchor %s from protobuf", protobuf_output_anchor.name
        )
        core_output_anchor = AMPOutputAnchor(
            protobuf_output_anchor.name,
            num_connections=protobuf_output_anchor.num_connections or 0,
        )

        if (
            protobuf_output_anchor.options
            != ProtobufOutputAnchor.OutgoingAnchorOptions.ORDERED
        ):
            raise ValueError("Only ordered output anchors are supported.")
        logger.debug("Deserialized Output Anchor %s from protobuf", core_output_anchor)
        return core_output_anchor

    @staticmethod
    def to_protobuf(
        output_anchor: "AMPOutputAnchor",
        anchor_options: ProtobufOutputAnchor.OutgoingAnchorOptions = ProtobufOutputAnchor.OutgoingAnchorOptions.ORDERED,
        record_limit: int = sys.maxsize,
    ) -> ProtobufOutputAnchor:
        """
        Given an AMPOutputAnchor, return a protobuf representation.

        Parameters
        ----------
        output_anchor
            AMP Output Anchor object to be serialized into protobuf.
        anchor_options
            Anchor must receive packets in the order that they came in.
        record_limit
            Max number of records the anchor can receive.

        Returns
        -------
        ProtobufMetadata
            The Protobuf representation of the AMP Metadata object.
        """
        metadata = (
            MetadataBuilder.to_protobuf(output_anchor.metadata)
            if output_anchor.is_open
            else None
        )
        logger.debug("Serialized metadata %s to protobuf", metadata)
        protobuf_output_anchor = ProtobufOutputAnchor(
            name=output_anchor.name,
            num_connections=output_anchor.num_connections,
            metadata=metadata,
            options=anchor_options,
            record_limit=record_limit,
        )
        logger.debug("Serialized Ouptut Anchor %s to protobuf", output_anchor.name)
        return protobuf_output_anchor
