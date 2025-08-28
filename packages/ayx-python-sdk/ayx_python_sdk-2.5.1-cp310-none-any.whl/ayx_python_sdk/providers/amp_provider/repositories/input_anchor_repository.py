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
"""Class that implements the Input Anchor repository singleton."""
import logging
from typing import Dict, List, TYPE_CHECKING, cast

from ayx_python_sdk.providers.amp_provider.builders.input_anchor_builder import (
    InputAnchorBuilder,
)
from ayx_python_sdk.providers.amp_provider.repositories.input_connection_repository import (
    InputConnectionRepository,
)
from ayx_python_sdk.providers.amp_provider.repositories.singleton import Singleton

if TYPE_CHECKING:
    from ayx_python_sdk.providers.amp_provider.amp_input_anchor import AMPInputAnchor
    from ayx_python_sdk.providers.amp_provider.resources.generated.incoming_anchor_pb2 import (
        IncomingAnchor as ProtobufInputAnchor,
    )


logger = logging.getLogger(__name__)


class InputAnchorRepository(metaclass=Singleton):
    """Class defines methods and properties to read/write/delete input anchors."""

    def __init__(self) -> None:
        self._repository: Dict[str, "AMPInputAnchor"] = {}

    def save_grpc_anchor(self, input_anchor: "ProtobufInputAnchor") -> None:
        """
        Convert an Input Anchor from Protobuf to AMP and saves it to the repository.

        Parameters
        ----------
        input_anchor
            The protobuf representation of an input anchor to be saved.
        """
        core_input_anchor = InputAnchorBuilder.from_protobuf(input_anchor)
        self.save_anchor(core_input_anchor)

    def save_anchor(self, anchor: "AMPInputAnchor") -> None:
        """
        Save AMP input anchor to repository.

        Parameters
        ----------
        anchor
            The AMPInputAnchor to be saved.
        """
        from ayx_python_sdk.providers.amp_provider import AMPInputConnection

        logger.debug("Saving Input Anchor %s to repository", anchor.name)
        self._repository[anchor.name] = anchor
        logger.debug("Current InputAnchorRepository State: %s", self._repository)

        connections = cast(List[AMPInputConnection], anchor.connections)
        for connection in connections:
            InputConnectionRepository().save_connection(anchor.name, connection)

    def get_anchor(self, anchor_name: str) -> "AMPInputAnchor":
        """
        Retrieve InputAnchor object associated with the anchor name.

        Parameters
        ----------
        anchor_name
            The name of the anchor to fetch from the repository.

        Returns
        -------
            The input anchor object with corresponding name.
        """
        if anchor_name in self._repository:
            return self._repository[anchor_name]
        else:
            raise ValueError(f"Anchor {anchor_name} does not exist")

    def delete_anchor(self, anchor_name: str) -> None:
        """
        Delete InputAnchor object associated with the anchor name.

        Parameters
        ----------
        anchor_name
            The name of the anchor to delete from the repository.
        """
        if anchor_name in self._repository:
            logger.debug("Removing Input Anchor %s from repository", anchor_name)
            del self._repository[anchor_name]
            logger.debug("Current InputAnchorRepository State: %s", self._repository)
        else:
            raise ValueError(f"Anchor {anchor_name} does not exist")

    def clear_repository(self) -> None:
        """Delete all data in the repository."""
        logger.debug("Clearing InputAnchorRepository")
        self._repository = {}
