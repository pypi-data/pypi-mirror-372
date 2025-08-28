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
"""Utility definitions."""
from typing import TYPE_CHECKING

from ayx_python_sdk.core.constants import NULL_VALUE_PLACEHOLDER

from .utilities import convert_metadata_to_record_info, convert_record_info_to_metadata

if TYPE_CHECKING:
    import pandas as pd


def fill_df_nulls_with_blackbird_nulls(df: "pd.DataFrame") -> None:
    """Fill all dataframe null values with blackbird's representation."""
    df.fillna(NULL_VALUE_PLACEHOLDER, inplace=True)


__all__ = [
    "convert_metadata_to_record_info",
    "convert_record_info_to_metadata",
    "fill_df_nulls_with_blackbird_nulls",
    "NULL_VALUE_PLACEHOLDER",
]
