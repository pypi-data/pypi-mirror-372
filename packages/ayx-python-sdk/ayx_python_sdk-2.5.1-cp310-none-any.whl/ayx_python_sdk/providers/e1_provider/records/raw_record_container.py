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
"""RawRecordContainer class definition."""
from typing import Dict, List, Optional, TYPE_CHECKING

from AlteryxPythonSDK import RecordCreator, RecordInfo, RecordRef

from ayx_python_sdk.providers.e1_provider.proxies import (
    FieldProxy,
    RecordCopierProxy,
)
from ayx_python_sdk.providers.e1_provider.records.base_record_container import (
    BaseRecordContainer,
)
from ayx_python_sdk.providers.e1_provider.utilities import (
    fill_df_nulls_with_blackbird_nulls,
)


if TYPE_CHECKING:
    import pandas as pd


class RawRecordContainer(BaseRecordContainer):
    """Container for copying and holding raw records."""

    __slots__ = [
        "records",
        "_input_record_info",
        "_storage_record_info",
        "_field_map",
        "_record_copier",
        "_input_fields",
    ]

    def __init__(
        self,
        input_record_info: RecordInfo,
        storage_record_info: Optional[RecordInfo] = None,
        field_map: Optional[Dict[str, str]] = None,
    ) -> None:
        """Construct a container."""
        super().__init__()
        if (storage_record_info is None) ^ (field_map is None):
            raise ValueError(
                "storage_record_info and field_map must both be specified."
            )

        self._input_record_info = input_record_info

        if storage_record_info is None:
            self._storage_record_info = self._input_record_info.clone()
        else:
            self._storage_record_info = storage_record_info

        if field_map is None:
            self._field_map = {
                str(field.name): str(field.name) for field in self._storage_record_info
            }
        else:
            self._field_map = field_map

        self._record_copier = RecordCopierProxy(
            self._input_record_info, self._storage_record_info, self._field_map
        )
        self._input_fields = {
            field.name: FieldProxy(field) for field in input_record_info
        }
        self.records: List[RecordCreator] = []

    def add_record(self, record: RecordRef) -> None:
        """Make a copy of the record and add it to the container."""
        self.records.append(self._record_copier.copy(record))

    def build_dataframe(self) -> "pd.DataFrame":
        """Build a dataframe from the container."""
        raise NotImplementedError()

    def update_with_dataframe(self, df: "pd.DataFrame") -> None:
        """Update stored records with values from a dataframe."""
        num_rows, _ = df.shape

        if num_rows != len(self.records):
            raise ValueError(
                "Dataframe and source container must have the same number of records."
            )

        fill_df_nulls_with_blackbird_nulls(df)

        for record, (_, row) in zip(self.records, df.iterrows()):
            for column_name in list(df):
                try:
                    field = self._storage_record_info.get_field_by_name(column_name)
                    if field is None:
                        raise Exception()
                except Exception:
                    raise RuntimeError(
                        f"Couldn't update field '{column_name}' that does not exist"
                    )
                FieldProxy(field).set(record, row[column_name])
