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
"""Simple Record Packet class definition."""
from typing import TYPE_CHECKING

from ayx_python_sdk.core.metadata import Metadata
from ayx_python_sdk.core.record_packet_base import RecordPacketBase


if TYPE_CHECKING:
    import pandas as pd


class RecordPacket(RecordPacketBase):
    """
    Simple record packet based on pandas.

    This record packet is a generic format based on the pandas dataframe
    and the Record class.
    """

    def __init__(self, metadata: Metadata, df: "pd.DataFrame"):
        """
        Construct a record packet.

        Parameters
        ----------
        metadata
            The metadata for records contained in the packet.

        records
            Optional sequence of records for initializing data in the packet.
        """
        if len(df.columns) != len(metadata):
            raise ValueError(
                "Dataframe must have the same number of fields as metadata."
            )

        self._df = df
        self.__metadata = metadata

    @property
    def metadata(self) -> Metadata:
        """
        Get the packet metadata.

        Returns
        -------
        Metadata
            The metadata for records contained in the packet.
        """
        return self.__metadata

    def to_dataframe(self) -> "pd.DataFrame":
        """
        Get the packet data as a dataframe.

        Returns
        -------
        pd.DataFrame
            The dataframe that contains all records in the packet.
        """
        return self._df

    @classmethod
    def from_dataframe(cls, metadata: Metadata, df: "pd.DataFrame") -> "RecordPacket":
        """
        Build a packet from a dataframe.

        Parameters
        ----------
        metadata
            The metadata for the record packet.
        df
            The dataframe to generate records from.
        """
        return cls(metadata, df)
