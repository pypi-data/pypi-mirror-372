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
"""Example pass through tool."""
from ayx_python_sdk.core import (
    Anchor,
    PluginV2,
)
from ayx_python_sdk.providers.amp_provider.amp_provider_v2 import AMPProviderV2

from pandas.core.dtypes.common import is_integer_dtype

from pyarrow import RecordBatch, Table


class AyxSdkMultipleOutputAnchors(PluginV2):
    """A sample Plugin that filters numeric data for odd and even values."""

    def __init__(self, provider: "AMPProviderV2"):
        """Construct the plugin."""
        self.provider = provider
        self.provider.io.info("AyxSdkMultipleOutputAnchors tool started.")

    def on_record_batch(self, batch: "Table", anchor: "Anchor") -> None:
        """
        Process the passed record batch.

        The method that gets called whenever the plugin receives a record batch on an input.

        This method IS NOT called during update-only mode.

        Parameters
        ----------
        batch
            A pyarrow Table containing the received batch.
        anchor
            A namedtuple('Anchor', ['name', 'connection']) containing input connection identifiers.
        """
        metadata = batch.schema
        if not any([field_name == "Value" for field_name in metadata.names]):
            raise RuntimeError(
                "Incoming data must contain a column with the name 'Value'"
            )
        input_dataframe = batch.to_pandas()

        if not is_integer_dtype(input_dataframe["Value"]):
            raise RuntimeError("'Value' column must be of 'int' data type")

        grouped = input_dataframe.groupby("Value")
        odds = grouped.filter(lambda row: (row["Value"] % 2 == 1).any())
        evens = grouped.filter(lambda row: (row["Value"] % 2 == 0).any())

        odd_batch = RecordBatch.from_pandas(odds, preserve_index=False)
        even_batch = RecordBatch.from_pandas(evens, preserve_index=False)
        self.provider.write_to_anchor("Output1", odd_batch)
        self.provider.write_to_anchor("Output2", even_batch)

    def on_incoming_connection_complete(self, anchor: "Anchor") -> None:
        """
        Call when an incoming connection is done sending data including when no data is sent on an optional input anchor.

        This method IS NOT called during update-only mode.

        Parameters
        ----------
        anchor
            NamedTuple containing anchor.name and anchor.connection.
        """
        self.provider.io.info(
            f"Received complete update from {anchor.name}:{anchor.connection}."
        )

    def on_complete(self) -> None:
        """
        Clean up any plugin resources, or push records for an input tool.

        This method gets called when all other plugin processing is complete.

        In this method, a Plugin designer should perform any cleanup for their plugin.
        However, if the plugin is an input-type tool (it has no incoming connections),
        processing (record generation) should occur here.

        Note: A tool with an optional input anchor and no incoming connections should
        also write any records to output anchors here.
        """
        self.provider.io.info("AyxSdkMultipleOutputAnchors tool done.")
