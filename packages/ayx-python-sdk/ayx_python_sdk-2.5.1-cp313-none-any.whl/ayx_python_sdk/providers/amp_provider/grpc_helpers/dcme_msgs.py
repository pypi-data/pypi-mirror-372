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
"""AMP Provider: Proxy class for DCM API."""
import datetime as dt
from typing import Dict, Optional

from ayx_python_sdk.core.exceptions import DcmEError, DcmEException
from ayx_python_sdk.providers.amp_provider.resources.generated.dcm_e_pb2 import (
    DcmERequest,
    DcmEResponse,
)

from google.protobuf import json_format
from google.protobuf.struct_pb2 import Struct

from .control_msgs import DCME_REQ, ctrl_out_wrapper


@ctrl_out_wrapper(DCME_REQ, set_id=True)
def get_connection_msg(connection_id: str) -> DcmERequest:  # noqa: D102
    """Create a connection request message."""
    req = DcmERequest()
    req.v2.get_connection.connection_id = connection_id
    return req


@ctrl_out_wrapper(DCME_REQ, set_id=True)
def get_write_lock_msg(
    connection_id: str,
    role: str,
    secret_type: str,
    expires_in: Optional[dt.datetime] = None,
) -> DcmERequest:  # noqa: D102
    """Create a LockSecret message."""
    req = DcmERequest()
    req.v2.lock_secret.connection_id = connection_id
    req.v2.lock_secret.credential_role = role
    req.v2.lock_secret.secret_type = secret_type
    if expires_in:
        req.v2.lock_secret.expires_in = expires_in.isoformat()
    return req


@ctrl_out_wrapper(DCME_REQ, set_id=True)
def free_write_lock_msg(
    connection_id: str, role: str, secret_type: str, lock_id: str
) -> DcmERequest:  # noqa: D102
    """Create a UnlockSecret message."""
    req = DcmERequest()
    req.v2.unlock_secret.connection_id = connection_id
    req.v2.unlock_secret.credential_role = role
    req.v2.unlock_secret.secret_type = secret_type
    req.v2.unlock_secret.lock_id = lock_id
    return req


@ctrl_out_wrapper(DCME_REQ, set_id=True)
def update_connection_secret_msg(
    connection_id: str,
    lock_id: str,
    role: str,
    secret_type: str,
    value: str,
    expires_on: Optional[dt.datetime],
    parameters: Optional[Dict[str, str]],
) -> DcmERequest:  # noqa: D102
    """Create UpdateSecret message."""
    req = DcmERequest()
    req.v2.update_secret.connection_id = connection_id
    req.v2.update_secret.lock_id = lock_id
    req.v2.update_secret.credential_role = role
    req.v2.update_secret.secret_type = secret_type
    req.v2.update_secret.value = value
    if parameters:
        st = Struct()
        st.update(parameters)
        req.v2.update_secret.parameters.CopyFrom(st)
        if expires_on:
            req.v2.update_secret.expires_on = expires_on.isoformat()
    return req


def handle_response(res: DcmEResponse) -> Dict:
    """Handle DcmE response."""
    response_dict = json_format.MessageToDict(res.response)
    if not res.success:
        if "message" in response_dict.keys() and "errorCode" in response_dict.keys():
            if "detail" in response_dict.keys():
                response_dict["dcme_exception"] = DcmEException(
                    "Dcm.E Error!",
                    DcmEError(
                        response_dict["message"],
                        int(response_dict["errorCode"]),
                        response_dict["detail"],
                    ),
                )
            else:
                response_dict["dcme_exception"] = DcmEException(
                    "Dcm.E Error!",
                    DcmEError(
                        response_dict["message"], int(response_dict["errorCode"])
                    ),
                )
        else:
            response_dict["dcme_exception"] = DcmEException(
                "Dcm.E Error!", DcmEError(res.response, 10003)
            )
    return response_dict
