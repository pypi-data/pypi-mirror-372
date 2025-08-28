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
"""ParsedRecordContainer class definition."""
from typing import Any, List, Optional, TYPE_CHECKING

from AlteryxPythonSDK import RecordInfo, RecordRef

from .base_record_container import BaseRecordContainer
from ..proxies import FieldProxy

if TYPE_CHECKING:
    import pandas as pd


class ParsedRecordContainer(BaseRecordContainer):
    """Container for parsing and holding parsed records."""

    __slots__ = ["records", "_input_fields", "_field_names_to_parse", "_parse_fields"]

    def __init__(
        self,
        input_record_info: RecordInfo,
        field_names_to_parse: Optional[List[str]] = None,
    ) -> None:
        """Construct a container."""
        self._input_fields = {
            field.name: FieldProxy(field) for field in input_record_info
        }

        if field_names_to_parse is None:
            self._field_names_to_parse = [field.name for field in input_record_info]
        else:
            self._field_names_to_parse = field_names_to_parse

        self._parse_fields = [
            self._input_fields[field_name] for field_name in self._field_names_to_parse
        ]

        self.records: List[List[Any]] = []

    def add_record(self, record: RecordRef) -> None:
        """Add a new record to the container and parse it."""
        self.records.append(self._parse_record(record))

    def _parse_record(self, record: RecordRef) -> List[Any]:
        return [field.get(record) for field in self._parse_fields]

    def build_dataframe(self) -> "pd.DataFrame":
        """Build a dataframe out of the parsed records."""
        import pandas as pd

        return pd.DataFrame(self.records, columns=self._field_names_to_parse)

    def update_with_dataframe(self, df: "pd.DataFrame") -> None:
        """Update container with a dataframe."""
        raise NotImplementedError()
