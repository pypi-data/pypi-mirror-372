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
"""The file provider input anchor class definition."""
from typing import List, Optional, TYPE_CHECKING

from ayx_python_sdk.core.doc_utilities import inherit_docs
from ayx_python_sdk.core.input_anchor_base import InputAnchorBase

if TYPE_CHECKING:  # noqa: F401
    from ayx_python_sdk.core.input_connection_base import (  # noqa: F401
        InputConnectionBase,
    )  # noqa: F401


@inherit_docs
class FileProviderInputAnchor(InputAnchorBase):
    """An input anchor that contains input connection information."""

    def __init__(
        self,
        name: str,
        allow_multiple: bool = False,
        optional: bool = False,
        connections: Optional[List["InputConnectionBase"]] = None,
    ) -> None:
        """
        Instantiate a file provider input anchor.

        Parameters
        ----------
        name
            The name of the input anchor.
        allow_multiple
            Indicates whether the anchor can have multiple input connections associated with it.
        optional
            Indicates whether the anchor is optional or not.
        connections
            The list of input connections associated with this anchor.
        """
        self.__name = name
        self.__allow_multiple = allow_multiple
        self.__optional = optional
        self.__connections: List["InputConnectionBase"] = connections or []

    @property
    def name(self) -> str:  # noqa: D102
        return self.__name

    @property
    def allow_multiple(self) -> bool:  # noqa: D102
        return self.__allow_multiple

    @property
    def optional(self) -> bool:  # noqa: D102
        return self.__optional

    @property
    def connections(self) -> List["InputConnectionBase"]:  # noqa: D102
        return self.__connections
