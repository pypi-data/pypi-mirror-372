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
"""Mock record ref class definition."""
from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .record_info import RecordInfo


class RecordRef:
    """Record ref mock."""

    def __init__(self, record_info: "RecordInfo") -> None:
        """Construct a record ref."""
        self.data: Dict[str, Any] = {field.name: None for field in record_info}
        self.record_info = record_info

    def set_field(self, name: str, value: Any) -> None:
        """Set a field to a value."""
        self.data[name] = value

    def get_field(self, name: str) -> Any:
        """Get the value of a field."""
        return self.data[name]

    def __eq__(self, other: object) -> bool:
        """Compare two record refs for equality."""
        if not isinstance(other, RecordRef):
            return NotImplemented

        return self.data == other.data
