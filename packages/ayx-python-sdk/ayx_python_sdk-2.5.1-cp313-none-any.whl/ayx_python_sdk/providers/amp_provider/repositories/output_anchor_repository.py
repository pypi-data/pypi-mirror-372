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
"""Repository for output anchor GRPC."""
import logging
from typing import Dict, List, TYPE_CHECKING

from ayx_python_sdk.providers.amp_provider.builders.output_anchor_builder import (
    OutputAnchorBuilder,
)
from ayx_python_sdk.providers.amp_provider.repositories.singleton import Singleton


if TYPE_CHECKING:
    from ayx_python_sdk.providers.amp_provider.amp_output_anchor import (
        AMPOutputAnchor as CoreOutputAnchor,
    )
    from ayx_python_sdk.providers.amp_provider.resources.generated.outgoing_anchor_pb2 import (
        OutgoingAnchor as GrpcOutputAnchor,
    )


logger = logging.getLogger(__name__)


class OutputAnchorRepository(metaclass=Singleton):
    """Repository class, output anchors."""

    _output_anchor_builder = OutputAnchorBuilder()

    def __init__(self) -> None:
        self._repository: Dict[str, "CoreOutputAnchor"] = {}

    def save_anchor(self, anchor: "CoreOutputAnchor") -> None:
        """
        Save an AMPOutputAnchor object to the repository.

        Parameters
        ----------
        anchor
            The AMP output anchor to save to the repository.
        """
        logger.debug("Adding anchor %s to OutputAnchorRepository", anchor.name)
        self._repository[anchor.name] = anchor
        logger.debug("Current OutputAnchorRepository State: %s", self._repository)

    def get_anchor(self, anchor_name: str) -> "CoreOutputAnchor":
        """
        Retrieve an AMPOutputAnchor object from the repository if it's already been saved.

        Parameters
        ----------
        anchor_name
            The name of the output anchor to get from the repository.

        Returns
        -------
        CoreOutputAnchor
            The retrieved output anchor that corresponds to the anchor name.
        """
        if anchor_name not in self._repository:
            raise ValueError(f"Anchor {anchor_name} does not exist")
        return self._repository[anchor_name]

    def delete_anchor(self, anchor_name: str) -> None:
        """
        Remove an AMPOutputAnchor object from the repository if it's already been saved.

        Parameters
        ----------
        anchor_name
            The name of the output anchor to delete from the repository.
        """
        if anchor_name not in self._repository:
            raise ValueError(f"Anchor {anchor_name} can't be deleted, it doesn't exist")
        logger.debug("Removing anchor %s from OutputAnchorRepository", anchor_name)
        del self._repository[anchor_name]
        logger.debug("Current OutputAnchorRepository State: %s", self._repository)

    def save_grpc_anchor(self, anchor: "GrpcOutputAnchor") -> None:
        """
        Save a protobuf Output Anchor to the repository.

        Parameters
        ----------
        anchor
            The grpc representation of the output anchor.
        """
        core_anchor = self._output_anchor_builder.from_protobuf(anchor)
        self.save_anchor(anchor=core_anchor)

    def clear_repository(self) -> None:
        """Delete all data in the repository."""
        logger.debug("Clearing OutputAnchorRepository")
        self._repository = {}
        logger.debug("Current OutputAnchorRepository State: %s", self._repository)

    def get_all_anchor_names(self) -> List[str]:
        """
        Pull a list of all anchor names in the repository.

        Returns
        -------
        List[str]
            List of all anchor names that exist in the repository.
        """
        return list(self._repository.keys())
