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
import logging
from functools import wraps
from typing import Callable, Dict, TYPE_CHECKING
from uuid import uuid4

from ayx_python_sdk.providers.amp_provider.resources.generated.outgoing_metadata_push_pb2 import (
    OutgoingMetadataPush,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.output_message_data_pb2 import (
    OutputMessageData,
    OutputMessageTypes,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.password_data_pb2 import (
    PasswordData,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.sdk_tool_service_v2_pb2 import (
    ControlOut,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.translate_message_data_pb2 import (
    TranslateMessageData,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.update_progress_pb2 import (
    UpdateProgress,
)

if TYPE_CHECKING:
    from pyarrow import Schema  # noqa F401


OUTPUT_MSG = "output_message"
TRANSLATED_MSG = "translated_message"
TRANSLATE_MSG = "translate_message"
DECRYPT_PW = "decrypt_password"
DCME_REQ = "dcm_e_request"
METADATA_MSG = "outgoing_metadata"
UPDATE_MSG = "update_progress"

ACCEPTED_PAYLOADS = set(
    [OUTPUT_MSG, TRANSLATE_MSG, DECRYPT_PW, DCME_REQ, METADATA_MSG, UPDATE_MSG]
)

logger = logging.getLogger()


def ctrl_out_wrapper(which_payload: str, set_id: bool = False) -> Callable:
    """Wrap a payload, returned by the decorated function, in a ControlOut message."""

    def _inner(func: Callable) -> Callable:
        @wraps(func)
        def set_payload(*args: tuple, **kwargs: dict) -> ControlOut:
            if which_payload not in ACCEPTED_PAYLOADS:
                logger.error("Can not assign CtrlOut payload %s", which_payload)
                raise AttributeError
            msg = ControlOut()
            if set_id:
                msg.msg_id = str(uuid4())
            ptr_msg_payload = getattr(msg, which_payload)
            ptr_msg_payload.CopyFrom(func(*args, **kwargs))
            return msg

        return set_payload

    return _inner


def _output_msg_data(control_values: Dict) -> ControlOut:
    return ControlOut(output_message=OutputMessageData(**control_values))


def _translate_msg(control_values: Dict) -> ControlOut:
    ctrl_out_msg = ControlOut(translate_message=TranslateMessageData(**control_values))
    ctrl_out_msg.msg_id = str(uuid4())
    return ctrl_out_msg


def _decrypt_password(control_values: Dict) -> ControlOut:
    msg = ControlOut(decrypt_password=PasswordData(**control_values))
    msg.msg_id = str(uuid4())
    return msg


def _confirm_complete() -> ControlOut:
    msg = ControlOut()
    msg.confirm_complete.SetInParent()
    return msg


ctrl_out_payload_fn = {
    OUTPUT_MSG: _output_msg_data,
    TRANSLATE_MSG: _translate_msg,
    DECRYPT_PW: _decrypt_password,
}


def new_control_out_msg(control_values: dict, oneof_key: str) -> ControlOut:
    """Create a ControlOut msg from passed values and payload key."""
    if oneof_key == "confirm_complete":
        return _confirm_complete()
    new_msg_w_payload = ctrl_out_payload_fn[oneof_key]
    return new_msg_w_payload(control_values)


@ctrl_out_wrapper(OUTPUT_MSG)
def new_ctrl_out_error_msg(err_msg: str, priority: int) -> ControlOut:
    """Create a message with the Error type flag."""
    msg_data = {
        "message_type": OutputMessageTypes.OMT_Error,
        "message": err_msg,
        "priority": priority,
    }
    return OutputMessageData(**msg_data)


@ctrl_out_wrapper(OUTPUT_MSG)
def new_ctrl_out_info_msg(info_msg: str, priority: int) -> ControlOut:
    """Create a message with the Info type flag."""
    msg_data = {
        "message_type": OutputMessageTypes.OMT_Info,
        "message": info_msg,
        "priority": priority,
    }
    return OutputMessageData(**msg_data)


@ctrl_out_wrapper(OUTPUT_MSG)
def new_ctrl_out_warn_msg(warn_msg: str, priority: int) -> ControlOut:
    """Create a message with the Warn type flag."""
    msg_data = {
        "message_type": OutputMessageTypes.OMT_Warning,
        "message": warn_msg,
        "priority": priority,
    }
    return OutputMessageData(**msg_data)


@ctrl_out_wrapper(OUTPUT_MSG)
def new_ctrl_out_save_config(tool_config: str) -> ControlOut:
    """Create a message with the Warn type flag."""
    msg_data = {
        "message_type": OutputMessageTypes.OMT_UpdateOutputConfigXml,
        "message": tool_config,
    }
    return OutputMessageData(**msg_data)


@ctrl_out_wrapper(TRANSLATE_MSG, set_id=True)
def new_ctrl_out_translate_msg(msg: str, *args) -> ControlOut:  # type: ignore
    """Create a ControlOut.translate_message."""
    msg_data = {
        "unlocalized_string": msg,
        "interpolation_data": [str(arg) for arg in args] if len(args) > 0 else [],
    }
    return TranslateMessageData(**msg_data)


@ctrl_out_wrapper(DECRYPT_PW, set_id=True)
def new_ctrl_out_decrypt_msg(pw: str) -> ControlOut:
    """Create ControlOut.decrypt_password."""
    return PasswordData(password=pw)


@ctrl_out_wrapper(METADATA_MSG)
def new_ctrl_out_metadata_msg(anchor_name: str, metadata: "Schema") -> ControlOut:
    """Create ControlOut.outgoing_metadata_push."""
    as_bytes = metadata.serialize().to_pybytes()
    return OutgoingMetadataPush(output_anchor_name=anchor_name, schema=as_bytes)


@ctrl_out_wrapper(UPDATE_MSG)
def new_ctrl_out_update_progress_msg(progress: float) -> ControlOut:
    """Create ControlOut.outgoing_metadata_push."""
    msg_data = {
        "value": progress,
    }
    return UpdateProgress(**msg_data)
