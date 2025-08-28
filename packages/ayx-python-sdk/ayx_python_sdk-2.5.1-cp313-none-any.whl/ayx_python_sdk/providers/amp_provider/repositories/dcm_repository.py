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
"""Class that saves and retrieves AMP DCM information."""
import datetime as dt
import logging
from typing import Dict, Optional

from ayx_python_sdk.core.exceptions import DcmEError, DcmEException
from ayx_python_sdk.providers.amp_provider.repositories.singleton import Singleton
from ayx_python_sdk.providers.amp_provider.resources.generated.dcm_e_pb2 import (
    DcmERequest,
    DcmEResponse,
)

from google.protobuf import json_format

import grpc

logger = logging.getLogger(__name__)


class DCMRepository(metaclass=Singleton):
    """Repository that stores DCM information."""

    from ayx_python_sdk.providers.amp_provider.resources.generated.sdk_engine_service_pb2_grpc import (
        SdkEngineStub,
    )

    @staticmethod
    def __get_grpc_client() -> "SdkEngineStub":
        """
        Get grpc sdk engine client.

        Parameters
        ----------
        -
        """
        from ayx_python_sdk.providers.amp_provider.repositories.grpc_repository import (
            GrpcRepository,
        )

        try:
            return GrpcRepository().get_sdk_engine_client()
        except ValueError:
            raise DcmEException(
                "Error getting GRPC client!",
                DcmEError("Error getting GRPC client!", 10001),
            )

    @staticmethod
    def __handle_response(res: DcmEResponse) -> Dict:
        """Handle DcmE response."""
        response_dict = json_format.MessageToDict(res.response)
        if not res.success:
            if (
                "message" in response_dict.keys()
                and "errorCode" in response_dict.keys()
            ):
                if "detail" in response_dict.keys():
                    raise DcmEException(
                        "Dcm.E Error!",
                        DcmEError(
                            response_dict["message"],
                            int(response_dict["errorCode"]),
                            response_dict["detail"],
                        ),
                    )
                else:
                    raise DcmEException(
                        "Dcm.E Error!",
                        DcmEError(
                            response_dict["message"], int(response_dict["errorCode"])
                        ),
                    )
            else:
                raise DcmEException("Dcm.E Error!", DcmEError(res.response, 10003))

        return response_dict

    @staticmethod
    def get_connection(connection_id: str) -> Dict:
        """
        Retrieve connection information including secrets by connection ID.

        Parameters
        ----------
        connection_id
            string with UUID of connection
        """
        logger.debug("Getting DCM connection for " + str(connection_id))
        client = DCMRepository.__get_grpc_client()

        try:
            req = DcmERequest()
            req.v2.get_connection.connection_id = connection_id
            res = client.Dcm(req)
        except grpc.RpcError:
            raise DcmEException(
                "Error getting DCM connection!",
                DcmEError("Error getting DCM connection!"),
                10002,
            )
        return DCMRepository.__handle_response(res)

    @staticmethod
    def update_connection_secret(
        connection_id: str,
        lock_id: str,
        role: str,
        secret_type: str,
        value: str,
        expires_on: Optional[dt.datetime],
        parameters: Optional[Dict[str, str]],
    ) -> Dict:
        """
        Update a single secret for role and secret_type to value as well as the optional expires_on and parameters.

        Parameters
        ----------
        connection_id
            A connection ID
        lock_id
            A lock ID acquired from get_write_lock()
        role
            A role such as ?oauth?
        secret_type
            A secret type such as ?oauth_token?
        value
            The new value to store for the secret
        expires_on
            (Optional) DateTime expiration of this secret
        parameters
            Dict of parameter values for this secret (this is arbitrary user data stored as JSON)
        """
        from google.protobuf.struct_pb2 import Struct

        logger.debug("Updating DCM connection secret for " + str(connection_id))
        client = DCMRepository.__get_grpc_client()

        try:
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
            res = client.Dcm(req)
        except grpc.RpcError:
            raise DcmEException(
                "Error getting DCM connection!",
                DcmEError("Error getting DCM connection!"),
                10002,
            )
        return DCMRepository.__handle_response(res)

    @staticmethod
    def get_write_lock(
        connection_id: str,
        role: str,
        secret_type: str,
        expires_in: Optional[dt.datetime],
    ) -> Dict:
        """
        Attempt to acquire an exclusive write lock.

        Parameters
        ----------
        connection_id
            string with UUID of connection
        role
            A role such as ?oauth?
        secret_type
            A secret type such as ?oauth_token?
        expires_in
            (Optional) A DateTime value in which to ask for the lock to be held for in milliseconds.
        """
        logger.debug("Getting DCM write lock for " + str(connection_id))
        client = DCMRepository.__get_grpc_client()

        try:
            req = DcmERequest()
            req.v2.lock_secret.connection_id = connection_id
            req.v2.lock_secret.credential_role = role
            req.v2.lock_secret.secret_type = secret_type
            if expires_in:
                req.v2.lock_secret.expires_in = expires_in.isoformat()
            res = client.Dcm(req)
        except grpc.RpcError:
            raise DcmEException(
                "Error getting DCM connection!",
                DcmEError("Error getting DCM connection!"),
                10002,
            )
        return DCMRepository.__handle_response(res)

    @staticmethod
    def free_write_lock(
        connection_id: str, role: str, secret_type: str, lock_id: str
    ) -> None:
        """
        Frees a lock obtained from a previous call to get_write_lock().

        Parameters
        ----------
        connection_id
            string with UUID of connection
        role
            A role such as ?oauth?
        secret_type
            A secret type such as ?oauth_token?
        lock_id
            A lock_id acquired from a previous call to get_write_lock()
        """
        logger.debug(
            "Freeing DCM write lock for "
            + str(connection_id)
            + " lock_id: "
            + str(lock_id)
        )
        client = DCMRepository.__get_grpc_client()

        try:
            req = DcmERequest()
            req.v2.unlock_secret.connection_id = connection_id
            req.v2.unlock_secret.credential_role = role
            req.v2.unlock_secret.secret_type = secret_type
            req.v2.unlock_secret.lock_id = lock_id
            res = client.Dcm(req)
        except grpc.RpcError:
            raise DcmEException(
                "Error getting DCM connection!",
                DcmEError("Error getting DCM connection!"),
                10002,
            )
        DCMRepository.__handle_response(res)
