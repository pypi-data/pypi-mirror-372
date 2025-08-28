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
"""Class that implements serialization/deserialization for Input Anchors to and from protobuf message format."""
import logging
from enum import Enum

from ayx_python_sdk.providers.amp_provider.amp_input_anchor import AMPInputAnchor
from ayx_python_sdk.providers.amp_provider.builders.input_connection_builder import (
    InputConnectionBuilder,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.incoming_anchor_pb2 import (
    IncomingAnchor as ProtobufInputAnchor,
)


class AnchorOptionsBitmask(Enum):
    """Bitfield values for anchor flags."""

    NONE = 0
    REQUIRED = 1
    ALLOW_MULTIPLE = 2
    REQUIRES_SEQUENCE = 4
    REQUEST_SEQUENCE = 8


logger = logging.getLogger(__name__)


class InputAnchorBuilder:
    """RPC Builder for converting protobuf Input Anchors to AMP Input Anchors and vice-versa."""

    _input_connection_builder = InputConnectionBuilder()

    @classmethod
    def to_protobuf(cls, amp_input_anchor: "AMPInputAnchor") -> ProtobufInputAnchor:
        """
        Serialize AMP input anchor to protobuf objects.

        Parameters
        ----------
        amp_input_anchor
            An AMPInputAnchor object to serialize into protobuf.

        Returns
        -------
        ProtobufInputAnchor
            The Protobuf representation of the passed in AMPInputAnchor.
        """
        protobuf_input_anchor = ProtobufInputAnchor()
        protobuf_input_anchor.name = amp_input_anchor.name
        logger.debug("Serializing input anchor %s to protobuf", amp_input_anchor.name)
        for connection in amp_input_anchor.connections:
            protobuf_connection = cls._input_connection_builder.to_protobuf(connection)
            protobuf_input_anchor.connections.append(protobuf_connection)
            logger.debug("Serializing connection %s to protobuf", connection.name)

        protobuf_input_anchor.sequencing = 0
        if not amp_input_anchor.optional:
            protobuf_input_anchor.sequencing |= AnchorOptionsBitmask.REQUIRED.value
        if amp_input_anchor.allow_multiple:
            protobuf_input_anchor.sequencing |= (
                AnchorOptionsBitmask.ALLOW_MULTIPLE.value
            )

        # For now, we only support REQUIRES_SEQUENCE
        protobuf_input_anchor.sequencing |= AnchorOptionsBitmask.REQUIRES_SEQUENCE.value
        logger.debug(
            "Input anchor %s has sequencing options %s",
            amp_input_anchor.name,
            bin(protobuf_input_anchor.sequencing),
        )
        return protobuf_input_anchor

    @classmethod
    def from_protobuf(
        cls, protobuf_input_anchor: ProtobufInputAnchor
    ) -> AMPInputAnchor:
        """
        Deserialize protobuf objects into AMP input anchor.

        Parameters
        ----------
        protobuf_input_anchor
            Protobuf object to be serialized into an AMPInputAnchor.

        Returns
        -------
        AMPInputAnchor
            The AMPInputAnchor representation of the protobuf object.
        """
        logger.debug("Deserializing input anchor %s", protobuf_input_anchor.name)
        allow_multiple = bool(
            protobuf_input_anchor.sequencing & AnchorOptionsBitmask.ALLOW_MULTIPLE.value
        )
        optional = not bool(
            protobuf_input_anchor.sequencing & AnchorOptionsBitmask.REQUIRED.value
        )

        amp_input_anchor = AMPInputAnchor(
            name=protobuf_input_anchor.name,
            allow_multiple=allow_multiple,
            optional=optional,
        )

        for connection in protobuf_input_anchor.connections:
            input_connection = cls._input_connection_builder.from_protobuf(
                connection, amp_input_anchor
            )
            amp_input_anchor.connections.append(input_connection)
            logger.debug("Deserialized input connection %s", input_connection.name)

        return amp_input_anchor
