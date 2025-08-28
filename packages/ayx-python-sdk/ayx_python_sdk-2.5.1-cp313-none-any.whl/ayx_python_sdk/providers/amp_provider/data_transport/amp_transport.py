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
"""Arrows stream formatted transport interface."""
import logging
from collections import defaultdict
from typing import Generator, TYPE_CHECKING, Tuple

from ayx_python_sdk.providers.amp_provider.data_transport.transport_base import (
    TransportBase,
)
from ayx_python_sdk.providers.amp_provider.grpc_helpers.record_transfer_msgs import (
    new_record_transfer_out_msg,
)

import pyarrow as pa

if TYPE_CHECKING:
    from ayx_python_sdk.providers.amp_provider.resources.generated.sdk_tool_service_v2_pb2 import (  # noqa: F401
        RecordTransferIn,
        RecordTransferOut,
    )

# Size of stream chunks, in n bytes.
# Desired 1MB default is causing some failures. Fairly sure this is on the slicing
# logic, and just needs better bounds to check so arrow doesn't freak out.
# Boxing that for another ticket after bigger stuff is done, though.
DEFAULT_CHUNK_SIZE = 1 * (10**6)


class AmpStreamTransport(TransportBase):
    """Transport interface to deliver data in arrows stream format."""

    logger = logging.getLogger()

    def __init__(self) -> None:
        self.stream_buffer: dict = defaultdict(dict)
        self.chunk_size = DEFAULT_CHUNK_SIZE
        self.incomplete_streams = 0

    # TODO: Rename this to something better for Transport interface.
    def send_record(
        self,
        record_batch: "pa.RecordBatch",
        anchor_name: str,
        connection_name: str = "",
    ) -> Generator["RecordTransferOut", None, None]:
        """Convert a given record batch into a sequence of RecordTransferOut msgs."""
        stream = self.get_rec_stream(record_batch)
        for chunk, end_of_chunk in self.iter_stream(stream):
            record_out = {
                "anchor_name": anchor_name,
                "data": chunk,
                "connection_name": connection_name,
                "end_of_chunk": end_of_chunk,
            }
            yield new_record_transfer_out_msg(record_out, "outgoing_records")

    def get_rec_stream(self, record_batch: "pa.RecordBatch") -> "pa.Buffer":
        """Get an arrows formatted stream buffer."""
        try:
            sink = pa.BufferOutputStream()
            writer = pa.ipc.new_stream(sink, record_batch.schema)
            writer.write(record_batch)
            writer.close()
        except Exception as e:
            self.logger.error(repr(e))
            raise e
        return sink.getvalue()

    def iter_stream(
        self, stream: "pa.Buffer"
    ) -> Generator[Tuple[bytes, bool], None, None]:
        """Break up a given stream by set chunk size."""
        buf = pa.BufferReader(stream)
        end_of_chunk = False
        while not end_of_chunk:
            end_of_chunk = buf.tell() + self.chunk_size >= buf.size()
            chunk = buf.read() if end_of_chunk else buf.read(self.chunk_size)
            yield (chunk, end_of_chunk)

    def _unpack_and_append_rec_in_payload(self, record_in: "RecordTransferIn") -> None:
        anchor_name = record_in.incoming_records.anchor_name
        connection_name = record_in.incoming_records.connection_name
        data = record_in.incoming_records.data
        if not self.stream_buffer[anchor_name].get(connection_name):
            self.incomplete_streams += 1
            self.stream_buffer[anchor_name][connection_name] = pa.BufferOutputStream()
        self.stream_buffer[anchor_name][connection_name].write(data)

    def _handle_completed_stream(self, record_in: "RecordTransferIn") -> None:
        self.logger.debug("Stream terminater received, completing batch.")
        anchor_name = record_in.incoming_records.anchor_name
        connection_name = record_in.incoming_records.connection_name
        data = self.stream_buffer[anchor_name][connection_name]
        try:
            reader = pa.ipc.open_stream(data.getvalue())
            self.stream_buffer[anchor_name][connection_name] = pa.BufferOutputStream()
            self.incomplete_streams -= 1
            return reader.read_all()
        except pa.ArrowException as ae:
            self.logger.error(
                "Exception caught reading completed batch chunk: %s", repr(ae)
            )
            raise ae

    def receive_record(self, record_in_msg: "RecordTransferIn") -> "pa.Table":
        """
        Receive RecordTransferIn messages.

        Returns None if the data received is only a chunk of a full record.
        Returns pa.Table if `end_of_chunk` is True.
        """
        self._unpack_and_append_rec_in_payload(record_in_msg)
        if record_in_msg.incoming_records.end_of_chunk:
            return self._handle_completed_stream(record_in_msg)
        return None
