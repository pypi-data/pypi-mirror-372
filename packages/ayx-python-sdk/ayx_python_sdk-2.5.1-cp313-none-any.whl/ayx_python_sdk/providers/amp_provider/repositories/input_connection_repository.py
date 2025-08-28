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
"""Class that saves input connection information given the associated anchor."""
import logging
from typing import Dict, List, Optional, TYPE_CHECKING

from ayx_python_sdk.core.input_connection_base import InputConnectionStatus
from ayx_python_sdk.providers.amp_provider.builders import InputConnectionBuilder
from ayx_python_sdk.providers.amp_provider.repositories.singleton import Singleton

if TYPE_CHECKING:
    from ayx_python_sdk.providers.amp_provider import (
        AMPInputAnchor,
        AMPInputConnection,
    )
    from ayx_python_sdk.providers.amp_provider.resources.generated.incoming_connection_pb2 import (
        IncomingConnection as ProtobufInputConnection,
    )


logger = logging.getLogger(__name__)


class InputConnectionRepository(metaclass=Singleton):
    """Repository that stores input connection information."""

    _input_connection_builder = InputConnectionBuilder()

    def __init__(self) -> None:
        """Initialize the input connection repository."""
        self._anchor_connection_map: Dict[str, List["AMPInputConnection"]] = {}
        self._connection_status_map: Dict[str, Dict[str, "InputConnectionStatus"]] = {}
        self._packet_size_map: Dict[str, Dict[str, Optional[int]]] = {}

    def save_connection(
        self, anchor_name: str, connection: "AMPInputConnection"
    ) -> None:
        """
        Save input connection information for the assoiciated anchor name.

        Parameters
        ----------
        anchor_name
            The name of the input anchor object that the connection is associated with.
        connection
            The AMPInputConnection object itself, to be saved to the repository.
        """
        self._anchor_connection_map.setdefault(anchor_name, [])
        logger.debug(
            "Adding connection %s to InputConnectionRepository for anchor %s",
            connection.name,
            anchor_name,
        )
        self._anchor_connection_map[anchor_name].append(connection)
        logger.debug(
            "Current InputConnectionRepository: %s", self._anchor_connection_map
        )
        if connection.metadata is None:
            raise ValueError(f"Input Connection {connection.name} is not open")
        from ayx_python_sdk.providers.amp_provider.repositories.input_metadata_repository import (
            InputMetadataRepository,
        )

        InputMetadataRepository().save_metadata(
            anchor_name, connection.name, connection.metadata
        )

    def save_grpc_connection(
        self, anchor: "AMPInputAnchor", connection: "ProtobufInputConnection"
    ) -> None:
        """
        Save input connection object given a protobuf object.

        Parameters
        ----------
        anchor
            The input anchor object that the connection is associated with.
        connection
            The protobuf representation of the input connection, to be serialized into AMP and saved to the repository.
        """
        amp_connection = self._input_connection_builder.from_protobuf(
            connection, anchor
        )
        self.save_connection(anchor.name, amp_connection)

    def get_all_connections(self, anchor_name: str) -> List["AMPInputConnection"]:
        """Get the connections associated with the given anchor name."""
        connections = self._anchor_connection_map.get(anchor_name)
        logger.debug(
            "Current InputConnectionRepository: %s", self._anchor_connection_map
        )
        if connections is None:
            raise ValueError(f"Anchor {anchor_name} not found in repository.")

        return connections

    def get_connection(
        self, anchor_name: str, connection_name: str
    ) -> "AMPInputConnection":
        """
        Get the connection associated with the given anchor name and connection name.

        Parameters
        ----------
        anchor_name
            The name of the anchor that the connection is associated with.
        connection_name
            The name of the input connection to retrieve.
        """
        connections = self.get_all_connections(anchor_name)
        logger.debug(
            "Searching connections on anchor %s for connection %s",
            anchor_name,
            connection_name,
        )
        for connection in connections:
            if connection.name == connection_name:
                return connection

        raise ValueError(
            f"Input connection {connection_name} not found in repository for anchor {anchor_name}."
        )

    def delete_connection(self, anchor_name: str, connection_name: str) -> None:
        """
        Delete the connection associated with the given anchor name and connection name.

        Parameters
        ----------
        anchor_name
            The name of the anchor that the connection is associated with.
        connection_name
            The name of the input connection to delete.
        """
        connections = self.get_all_connections(anchor_name)
        for idx, connection in enumerate(connections):
            if connection.name == connection_name:
                logger.debug(
                    "Removing connection %s from anchor %s in InputConnectionRepository",
                    connection_name,
                    anchor_name,
                )
                connections.pop(idx)
                if len(connections) == 0:
                    del self._anchor_connection_map[anchor_name]
                    logger.debug(
                        "Removing anchor %s from InputConnectionRepository", anchor_name
                    )
                return

        raise ValueError(
            f"Input connection {connection_name} not found in repository for anchor {anchor_name}."
        )

    def clear_repository(self) -> None:
        """Delete all data in the repository."""
        logger.debug("Clearing InputConnectionRepository")
        self._anchor_connection_map = {}
        self._packet_size_map = {}
        self._connection_status_map = {}
        logger.debug(
            "Current InputConnectionRepository: %s", self._anchor_connection_map
        )

    def save_connection_status(
        self, anchor_name: str, connection_name: str, status: "InputConnectionStatus"
    ) -> None:
        """
        Save input connection status associated with a given input connection/anchor name.

        Parameters
        ----------
        anchor_name
            The name of the anchor that the connection is associated with.
        connection_name
            The name of the input connection to set the status of.
        status
            Enumeration value (1,2,3, or 4) that corresponds to the status
            of this connection. (Created, Initialized, Receiving records, Closed)
        """
        logger.debug(
            "Updating connection status of anchor %s connection %s",
            anchor_name,
            connection_name,
        )
        self._connection_status_map.setdefault(anchor_name, {})
        self._connection_status_map[anchor_name][connection_name] = status

    def get_connection_status(
        self, anchor_name: str, connection_name: str
    ) -> "InputConnectionStatus":
        """
        Retrieve input connection status associated with a given input connection/anchor name.

        Parameters
        ----------
        anchor_name
            The name of the anchor that the connection is associated with.
        connection_name
            The name of the input connection to get the status of.

        Returns
        -------
        InputConnectionStatus
            Enumeration value (1,2,3, or 4) that corresponds to the status
            of this connection. (Created, Initialized, Receiving records, Closed)
        """
        if anchor_name not in self._connection_status_map:
            raise ValueError(f"Anchor {anchor_name} not found in repository")
        if connection_name not in self._connection_status_map[anchor_name]:
            raise ValueError(
                f"Status for connection {connection_name} not found in repository for anchor {anchor_name}."
            )
        status = self._connection_status_map[anchor_name][connection_name]
        return status

    def save_connection_packet_size(
        self, anchor_name: str, connection_name: str, size: Optional[int]
    ) -> None:
        """
        Save packet size associated with a given input connection/anchor name.

        Parameters
        ----------
        anchor_name
            The name of the anchor that the connection is associated with.
        connection_name
            The name of the input connection.
        size
            The max number of packets allowed.
        """
        logger.debug(
            "Updating packet size for anchor %s connection %s",
            anchor_name,
            connection_name,
        )
        self._packet_size_map.setdefault(anchor_name, {})
        self._packet_size_map[anchor_name][connection_name] = size

    def get_connection_packet_size(
        self, anchor_name: str, connection_name: str
    ) -> Optional[int]:
        """
        Retrieve packet size associated with a given input connection/anchor name.

        Parameters
        ----------
        anchor_name
            The name of the anchor that the connection is associated with.
        connection_name
            The name of the input connection to get the status of.

        Returns
        -------
        int, optional
            The max packet size on the conenction, if set, otherwise None.
        """
        if anchor_name not in self._packet_size_map:
            raise ValueError(f"Anchor {anchor_name} not found in repository")
        if connection_name not in self._packet_size_map[anchor_name]:
            raise ValueError(
                f"Packet size for connection {connection_name} not found in repository for anchor {anchor_name}."
            )
        size = self._packet_size_map[anchor_name][connection_name]
        return size
