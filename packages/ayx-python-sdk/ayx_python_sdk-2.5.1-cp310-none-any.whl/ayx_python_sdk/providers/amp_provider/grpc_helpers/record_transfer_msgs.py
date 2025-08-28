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
"""Helper functions to create record transfer message types."""

from ayx_python_sdk.providers.amp_provider.resources.generated.sdk_tool_service_v2_pb2 import (
    OutgoingRecords,
    RecordTransferOut,
    WantRecords,
)


def new_record_transfer_out_msg(
    record_values: dict, oneof_key: str
) -> RecordTransferOut:
    """Create a RecordTransferOut msg from passed values and payload key."""
    msg = RecordTransferOut()
    if oneof_key == "outgoing_records":
        msg = RecordTransferOut(outgoing_records=OutgoingRecords(**record_values))
    else:
        msg = RecordTransferOut(want_records=WantRecords(record_values["anchor_name"]))
    return msg
