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
"""Alteryx plugin output anchor definition."""
from typing import Callable, Iterable, Optional

import AlteryxPythonSDK as Sdk


class E1OutputAnchorProxy:
    """Output anchor definition."""

    __slots__ = [
        "engine_anchor_ref",
        "_metadata_pushed",
        "__record_info",
        "name",
        "allow_multiple",
        "optional",
        "num_connections",
        "push_records",
    ]

    def __init__(
        self,
        name: str,
        allow_multiple: bool,
        optional: bool,
        output_anchor_mgr: Sdk.OutputAnchorManager,
        record_info: Optional[Sdk.RecordInfo] = None,
    ) -> None:
        """Initialize an output anchor."""
        engine_anchor_ref_optional = output_anchor_mgr.get_output_anchor(name)
        if engine_anchor_ref_optional is None:
            raise RuntimeError(f"Can't find output anchor: {name}")
        else:
            self.engine_anchor_ref: Sdk.OutputAnchor = engine_anchor_ref_optional

        self._metadata_pushed: bool = False
        self.__record_info = record_info
        self.name = name
        self.allow_multiple = allow_multiple
        self.optional = optional
        self.num_connections: int = 0
        self.push_records: Callable = self._raise_metadata_error

    @property
    def record_info(self) -> Optional[Sdk.RecordInfo]:
        """Getter for record info."""
        return self.__record_info

    @record_info.setter
    def record_info(self, value: Sdk.RecordInfo) -> None:
        """Setter for record info."""
        if self._metadata_pushed:
            raise RuntimeError("Can't reassign record_info after it has been pushed.")

        self.__record_info = value

    def update_progress(self, percent: float) -> None:
        """Push the progress to downstream tools."""
        self.engine_anchor_ref.update_progress(percent)

    def push_metadata(self) -> None:
        """Push metadata to downstream tools."""
        if self.record_info is None:
            raise ValueError("record_info must be set before metadata can be pushed.")

        if not self._metadata_pushed:
            self.engine_anchor_ref.init(self.record_info)
            self._metadata_pushed = True
            self.push_records = self._push_records
        else:
            raise RuntimeError("Metadata is trying to be pushed a second time.")

    def _raise_metadata_error(self, _: Iterable[Sdk.RecordCreator]) -> None:
        """Push records out."""
        raise RuntimeError("Must run push_metadata before push_records can be called.")

    def _push_records(self, record_creators: Iterable[Sdk.RecordCreator]) -> None:
        """Push all records passed from iterable."""
        for record_creator in record_creators:
            self.engine_anchor_ref.push_record(record_creator.finalize_record(), False)

    def close(self) -> None:
        """Close the output anchor."""
        self.engine_anchor_ref.close()
