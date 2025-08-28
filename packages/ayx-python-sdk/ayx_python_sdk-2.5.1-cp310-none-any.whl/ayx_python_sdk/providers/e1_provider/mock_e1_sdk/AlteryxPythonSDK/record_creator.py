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
"""Mock record creator class definition."""
from typing import Any, TYPE_CHECKING

from .record_ref import RecordRef

if TYPE_CHECKING:
    from .record_info import RecordInfo


class RecordCreator:
    """Record Creator mock."""

    def __init__(self, record_info: "RecordInfo") -> None:
        """Construct a record creator."""
        self.record_ref = RecordRef(record_info)
        self.record_info = record_info

    def finalize_record(self) -> RecordRef:
        """Finalize a record ref."""
        return self.record_ref

    def reset(self, var_data_size: int = 0) -> None:
        """Reset the creator."""
        self.record_ref = RecordRef(self.record_info)

    def set_field(self, name: str, value: Any) -> None:
        """Set a field in the underlying record ref."""
        self.record_ref.set_field(name, value)
