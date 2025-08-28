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
"""Repository for gRPC objects."""
from typing import Optional, TYPE_CHECKING

from ayx_python_sdk.providers.amp_provider.repositories.singleton import Singleton

if TYPE_CHECKING:
    from grpc import Server
    from ayx_python_sdk.providers.amp_provider.grpc_util import SocketAddress
    from ayx_python_sdk.providers.amp_provider.resources.generated.sdk_engine_service_pb2_grpc import (
        SdkEngineStub,
    )


class GrpcRepository(metaclass=Singleton):
    """Class used to get the grpc client/server."""

    def __init__(self) -> None:
        """Construct the repository."""
        self._client: Optional["SdkEngineStub"] = None
        self._server: Optional["Server"] = None
        self._server_address: Optional["SocketAddress"] = None

    def save_sdk_engine_client(self, client: "SdkEngineStub") -> None:
        """
        Save the client.

        Parameters
        ----------
        client
            gRPC SdkEngineClient that can make calls to the services defined in the SdkEngineServicer.
        """
        self._client = client

    def get_sdk_engine_client(self) -> "SdkEngineStub":
        """
        Get the client.

        Returns
        -------
        SdkEngineStub
            The SdkEngineClient to make calls with.
        """
        if self._client is None:
            raise ValueError("Client has not been saved.")

        return self._client

    def save_sdk_tool_server(self, server: "Server") -> None:
        """
        Save the server.

        Parameters
        ----------
        server
            The SdkToolServer that is running on the Python process.
        """
        self._server = server

    def get_sdk_tool_server(self) -> "Server":
        """
        Get the server.

        Returns
        -------
        Server
            The SdkToolServer.
        """
        if self._server is None:
            raise ValueError("Server has not been saved.")

        return self._server

    def save_sdk_tool_server_address(self, address: "SocketAddress") -> None:
        """
        Save the server address.

        Parameters
        ----------
        address
            The IP address and port that the server is listening on.
        """
        self._server_address = address

    def get_sdk_tool_server_address(self) -> "SocketAddress":
        """
        Get the server address.

        Returns
        -------
        SocketAddress
            The IP address and port that the server is listening on.
        """
        if self._server_address is None:
            raise ValueError("Server address has not been saved.")

        return self._server_address

    def clear_sdk_engine_client(self) -> None:
        """Clear the client."""
        self._client = None

    def clear_repository(self) -> None:
        """Clear the repo."""
        self._client = None
        self._server = None
        self._server_address = None
