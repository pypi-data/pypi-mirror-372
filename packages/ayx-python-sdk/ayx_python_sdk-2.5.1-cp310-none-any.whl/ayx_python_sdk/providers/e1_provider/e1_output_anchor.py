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
from enum import Enum, unique
from typing import Iterator, Optional, TYPE_CHECKING

import AlteryxPythonSDK as Sdk


from ayx_python_sdk.core import OutputAnchorBase
from ayx_python_sdk.core.doc_utilities import inherit_docs
from ayx_python_sdk.core.metadata import Metadata
from ayx_python_sdk.core.record_packet import RecordPacket
from ayx_python_sdk.providers.e1_provider.e1_output_anchor_proxy import (
    E1OutputAnchorProxy,
)
from ayx_python_sdk.providers.e1_provider.e1_record_packet import E1RecordPacket
from ayx_python_sdk.providers.e1_provider.proxies.field_proxy import FieldProxy
from ayx_python_sdk.providers.e1_provider.utilities import (
    convert_metadata_to_record_info,
    fill_df_nulls_with_blackbird_nulls,
)

if TYPE_CHECKING:
    from ayx_python_sdk.core.record_packet_base import RecordPacketBase
    import pandas as pd


@unique
class OutputAnchorStatus(Enum):
    """Output anchor status enumeration."""

    CREATED = 0
    OPEN = 1
    CLOSED = 2


@inherit_docs
class E1OutputAnchor(OutputAnchorBase):
    """Output anchor definition."""

    __slots__ = ["_output_anchor_proxy", "_engine", "_metadata", "_status"]

    def __init__(
        self,
        output_anchor_proxy: E1OutputAnchorProxy,
        engine: Sdk.AlteryxEngine,
    ) -> None:
        """Initialize an output anchor."""
        self._output_anchor_proxy = output_anchor_proxy
        self._engine = engine
        self._metadata: Optional[Metadata] = None
        self._status = OutputAnchorStatus.CREATED

    @property
    def name(self) -> str:  # noqa: D102
        return self._output_anchor_proxy.name

    @property
    def allow_multiple(self) -> bool:  # noqa: D102
        return self._output_anchor_proxy.allow_multiple

    @property
    def optional(self) -> bool:  # noqa: D102
        return self._output_anchor_proxy.optional

    @property
    def num_connections(self) -> int:  # noqa: D102
        return self._output_anchor_proxy.num_connections

    @property
    def is_open(self) -> bool:
        """Get status indicating if the anchor is open."""
        return self._status == OutputAnchorStatus.OPEN

    @property
    def metadata(self) -> Optional["Metadata"]:
        """Get the anchor metadata."""
        return self._metadata

    def open(self, metadata: Metadata) -> None:  # noqa: D102
        if self._status.value > OutputAnchorStatus.CREATED.value:
            raise RuntimeError("Output anchor has already been opened.")

        self._metadata = metadata
        self._output_anchor_proxy.record_info = convert_metadata_to_record_info(
            metadata, self._engine
        )
        self._output_anchor_proxy.push_metadata()
        self._status = OutputAnchorStatus.OPEN

    def write(self, record_packet: "RecordPacketBase") -> None:  # noqa: D102
        if self._status != OutputAnchorStatus.OPEN:
            raise RuntimeError("Anchor must be opened before it can be written to.")

        if isinstance(record_packet, E1RecordPacket) or isinstance(
            record_packet, RecordPacket
        ):
            self._output_anchor_proxy.push_records(
                generate_records_from_df(
                    record_packet.to_dataframe(), self._output_anchor_proxy.record_info
                )
            )
        else:
            raise ValueError(
                "The E1 SDK Provider only supports E1RecordPacket and "
                "RecordPacket implementations of RecordPacketBase."
            )

    def flush(self) -> None:  # noqa: D102
        # The E1 Provider doesn't support flush, so just pass
        pass

    def close(self) -> None:  # noqa: D102
        if self._status != OutputAnchorStatus.OPEN:
            raise RuntimeError("Output anchor is not open, so it cannot be closed.")

        self._output_anchor_proxy.close()
        self._status = OutputAnchorStatus.CLOSED

    def update_progress(self, percent: float) -> None:  # noqa: D102
        if self._status != OutputAnchorStatus.OPEN:
            raise RuntimeError(
                "Output anchor must be open before progress can be written."
            )
        self._output_anchor_proxy.update_progress(percent)


def generate_records_from_df(
    df: "pd.DataFrame", record_info: Sdk.RecordInfo
) -> Iterator[Sdk.RecordCreator]:
    """Generate record creators from a dataframe."""
    fill_df_nulls_with_blackbird_nulls(df)
    columns = list(df)
    field_map = {field.name: FieldProxy(field) for field in record_info}
    fields = [field_map[column_name] for column_name in columns]

    record_creator = record_info.construct_record_creator()

    col_range = range(len(fields))
    for row in df.itertuples():
        record_creator.reset()
        for col_idx in col_range:
            fields[col_idx].set(record_creator, row[col_idx + 1])

        yield record_creator
