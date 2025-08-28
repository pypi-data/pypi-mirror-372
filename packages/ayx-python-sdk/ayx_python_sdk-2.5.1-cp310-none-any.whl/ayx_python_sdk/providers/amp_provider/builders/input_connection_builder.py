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
"""Class that implements the serialization/deserialization for input connection protobuf objects."""
import logging
from typing import TYPE_CHECKING

from ayx_python_sdk.providers.amp_provider.amp_input_connection import (
    AMPInputConnection,
)
from ayx_python_sdk.providers.amp_provider.builders.metadata_builder import (
    MetadataBuilder,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.incoming_connection_pb2 import (
    IncomingConnection as ProtobufIncomingConnection,
)


if TYPE_CHECKING:
    from ayx_python_sdk.providers import AMPInputAnchor
    from ayx_python_sdk.core import InputConnectionBase

logger = logging.getLogger(__name__)


class InputConnectionBuilder:
    """RPC Builder for transforming InputConnection into Protobuf messages and vice versa."""

    metadata_builder = MetadataBuilder()

    @classmethod
    def to_protobuf(
        cls, amp_input_connection: "InputConnectionBase"
    ) -> ProtobufIncomingConnection:
        """
        Serialize an AMPInputConnection object (amp_provider.amp_input_connection) into a Protobuf object.

        Parameters
        ----------
        amp_input_connection
            An AMPInputConnection object to serialize into protobuf.

        Returns
        -------
        ProtobufIncomingConnection
            The Protobuf representation of the passed in AMPInputConnection.
        """
        name = amp_input_connection.name
        if amp_input_connection.metadata is None:
            raise RuntimeError(
                "Input connection must be open in order to convert it to a Protobuf message."
            )

        logger.debug("Serializing %s to protobuf", amp_input_connection.metadata)
        metadata = cls.metadata_builder.to_protobuf(amp_input_connection.metadata)
        return ProtobufIncomingConnection(name=name, metadata=metadata)

    @classmethod
    def from_protobuf(
        cls,
        protobuf_input_connection: ProtobufIncomingConnection,
        amp_input_anchor: "AMPInputAnchor",
    ) -> AMPInputConnection:
        """
        Deserialize a Protobuf object into an AMPInputConnection object (amp_provider.amp_input_connection).

        Parameters
        ----------
        protobuf_input_connection
            Protobuf object to be serialized into an AMPInputAnchor.
        amp_input_anchor
            The AMPInputAnchor that the connection is associated with.

        Returns
        -------
        AMPInputConnection
            The AMPInputConnection representation of the protobuf object.
        """
        name = protobuf_input_connection.name
        logger.debug("Deserializing connection %s from protobuf", name)
        metadata = cls.metadata_builder.from_protobuf(
            protobuf_input_connection.metadata
        )
        logger.debug("Deserialized %s from protobuf", metadata)
        return AMPInputConnection(name, metadata, amp_input_anchor)
