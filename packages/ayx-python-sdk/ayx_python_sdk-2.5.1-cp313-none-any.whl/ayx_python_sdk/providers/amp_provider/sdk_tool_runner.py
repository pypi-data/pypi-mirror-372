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
"""Runner for the SDK gRPC lifecycle."""
import os
from typing import TYPE_CHECKING

from ayx_python_sdk.providers.amp_provider.grpc_util import build_sdk_tool_server
from ayx_python_sdk.providers.amp_provider.repositories.grpc_repository import (
    GrpcRepository,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.sdk_tool_service_startup_info_pb2 import (
    SdkToolServiceStartupInfo,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.transport_pb2 import (
    ReturnStatus,
)
from ayx_python_sdk.providers.amp_provider.utilities.constants import ToolEnvType
from ayx_python_sdk.providers.amp_provider.utilities.utilities import tool_type

if TYPE_CHECKING:
    from grpc.aio import Server


class HandshakeFailedException(RuntimeError):
    """Exception for when the handshake fails."""

    pass


# A well known token used to communicate the LISTENing port back
# to the owner process (OOP) on Desktop/Designer builds
# DO NOT CHANGE THIS STRING
# See also ToolProcess.cpp
LISTEN_PORT_TOKEN = "ListenPort: "


class SdkToolRunner:
    """Manage gRPC lifecycle for the SDK Plugin."""

    def __init__(self, sdk_engine_address: str):
        """Construct an SDK Tool Runner."""
        self._sdk_engine_address = sdk_engine_address
        self.sdk_tool_server: "Server" = None
        self.sdk_tool_server_address = sdk_engine_address

    async def start_service(self) -> None:
        """Start the SDK Tool Service."""
        socket_address = (
            os.getenv("TOOL_SERVICE_ADDRESS")
            if tool_type() == ToolEnvType.Service
            else "localhost:0"
        )

        [self.sdk_tool_server, port] = build_sdk_tool_server(socket_address)

        # See notes around LISTEN_PORT_TOKEN above. Explicit flush
        # ensures we do not buffer, but instead write directly to stdout.
        print(f"{LISTEN_PORT_TOKEN}{port}", flush=True)

        await self.sdk_tool_server.start()
        await self.sdk_tool_server.wait_for_termination()

    @staticmethod
    def handshake_with_sdk_engine_service() -> "ReturnStatus":
        """
        Run the handshake with the SDK Engine Server.

        Returns
        -------
        return_status: ReturnStatus
            Whether or not the handshake is successful

        Raises
        ------
        HandshakeFailedException
            If method cannot connect to the engine service
        """
        return_status = None
        if tool_type() == ToolEnvType.Desktop:
            try:
                return_status = (
                    GrpcRepository()
                    .get_sdk_engine_client()
                    .ConfirmSdkEngineServiceConnection(
                        SdkToolServiceStartupInfo(
                            success=True,
                            message=f"Startup of plugin successful!",
                            sdk_tool_server_address=GrpcRepository()
                            .get_sdk_tool_server_address()
                            .address,
                        ),
                    )
                )
            except Exception:
                raise HandshakeFailedException("Couldn't connect to server.")
        else:
            return_status = ReturnStatus(
                message=f"Connection successful!", success=True
            )
        return return_status

    async def wait_for_termination(self) -> None:
        """Block and wait for the process to terminate."""
        await self.sdk_tool_server.wait_for_termination()
