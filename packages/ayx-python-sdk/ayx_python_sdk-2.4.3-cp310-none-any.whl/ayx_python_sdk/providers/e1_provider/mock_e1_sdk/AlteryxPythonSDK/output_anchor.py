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
"""Mock output anchor class definition."""
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .record_info import RecordInfo
    from .record_ref import RecordRef


class OutputAnchor:
    """Output anchor mock."""

    def __init__(self) -> None:
        self.is_closed: bool = False
        self.record_info: Optional["RecordInfo"] = None
        self.pushed_records: List["RecordRef"] = []
        self.progress = 0.0

    def assert_close(self) -> None:
        """Assert the output anchor is closed."""
        assert self.is_closed

    def close(self) -> None:
        """Close the output anchor."""
        self.is_closed = True

    def init(self, record_info_out: "RecordInfo", sort_info_xml: str = "") -> bool:
        """Initialize the output anchor with record metadata."""
        self.record_info = record_info_out
        return True

    def output_record_count(self, final: bool) -> None:
        """Output the record count to Designer."""
        raise NotImplementedError()

    def push_record(self, record_ref: "RecordRef", no_auto_close: bool = False) -> bool:
        """Push a record downstream."""
        self.pushed_records.append(record_ref)
        return True

    def update_progress(self, percent: float) -> None:
        """Update progress."""
        self.progress = percent
