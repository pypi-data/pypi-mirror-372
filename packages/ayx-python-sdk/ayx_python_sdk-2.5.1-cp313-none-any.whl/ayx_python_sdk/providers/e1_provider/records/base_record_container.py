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
"""BaseRecordContainer class definition."""
from abc import ABC, abstractmethod
from typing import Any, List, TYPE_CHECKING


if TYPE_CHECKING:
    from AlteryxPythonSDK import RecordRef
    import pandas as pd


class BaseRecordContainer(ABC):
    """Container for records."""

    __slots__ = ["records"]

    def __init__(self) -> None:
        """Construct a record container."""
        self.records: List[Any] = []

    @abstractmethod
    def add_record(self, record: "RecordRef") -> None:
        """Make a copy of the record and add it to the container."""

    @abstractmethod
    def build_dataframe(self) -> "pd.DataFrame":
        """Build a dataframe from the records."""

    @abstractmethod
    def update_with_dataframe(self, df: "pd.DataFrame") -> None:
        """Update container with a dataframe."""

    def clear_records(self) -> None:
        """Clear all accumulated records."""
        self.records = []
