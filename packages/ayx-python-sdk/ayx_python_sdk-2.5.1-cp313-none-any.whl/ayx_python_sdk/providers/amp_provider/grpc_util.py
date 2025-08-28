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
"""Utility methods and classes for use with gRPC."""
import logging
import sys
from concurrent import futures
from typing import Any

from ayx_python_sdk.providers.amp_provider.resources.generated.sdk_engine_service_pb2_grpc import (
    SdkEngineStub,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.sdk_tool_service_v2_pb2_grpc import (
    SdkToolV2Stub,
    add_SdkToolV2Servicer_to_server,
)
from ayx_python_sdk.providers.amp_provider.sdk_tool_service_v2 import SdkToolServiceV2

import grpc

if sys.platform == "win32":
    from ayx_python_sdk.providers.amp_provider.cng_certs import read_windows_store_chain

logger = logging.getLogger(__name__)


def build_sdk_tool_server(sdk_tool_address: str):  # type: ignore
    """
    Build the SDK Tool Server.

    Parameters
    ----------
    sdk_tool_address: str
        A socket address that corresponds to the sdk tool.

    Returns
    -------
    server
        An instance of the SDK Tool Service gRPC server.

    sdk_tool_address
        A copy of the sdk_tool_address parameter, modified to point at server's open port.
    """
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ("grpc.max_send_message_length", -1),
            ("grpc.max_receive_message_length", -1),
        ],
    )
    add_SdkToolV2Servicer_to_server(SdkToolServiceV2(), server)
    # we are doing because fips() builtin exists only in Python FIPS special build
    try:
        fipsok: bool = fips()  # type: ignore # noqa
    except Exception:
        fipsok = False
    if fipsok and sys.platform == "win32":
        chain_pair = read_windows_store_chain("grpcio_alteryx_ssl")  # type: ignore
        server_credentials = grpc.ssl_server_credentials([chain_pair])
        port = server.add_secure_port(sdk_tool_address, server_credentials)
        logger.debug("FIPS mode enabled")
    else:
        port = server.add_insecure_port(sdk_tool_address)
    logger.debug(f"gRPC port: {port}")
    return server, port


def build_sdk_engine_client(sdk_engine_address: "SocketAddress") -> SdkToolV2Stub:
    """
    Build the SDK Engine Client.

    Parameters
    ----------
    sdk_engine_address: SocketAddress
        A socket address that corresponds to the sdk engine.

    Returns
    -------
    client
        An instance of the SDK Engine client
    """
    channel = grpc.insecure_channel(
        sdk_engine_address.address,
        options=[
            ("grpc.max_send_message_length", -1),
            ("grpc.max_receive_message_length", -1),
        ],
    )
    client = SdkEngineStub(channel)
    return client


class SocketAddress:
    """Class for tracking host and port information."""

    @classmethod
    def from_address_str(cls, address_str: str) -> "SocketAddress":
        """
        Construct a socket address from an address string.

        Parameters
        ----------
        address_str: str
            A string consisting of host and port, separated by a colon, such as "localhost:8000".

        Returns
        -------
        SocketAddress
            A new instance of the SocketAddress class.
        """
        host, port = address_str.split(":")
        return cls(host, int(port))

    def __init__(self, host: str, port: int) -> None:
        """
        Construct a socket address.

        Parameters
        ----------
        host: str
            The address hostname.

        port: int
            The address port.

        Returns
        -------
        SocketAddress
            A new instance of the SocketAddress class.
        """
        self.host = host
        self.port = port

    @property
    def address(self) -> str:
        """
        Get the address string that contains both host and port.

        Returns
        -------
        address: str
            The address string in the form "host:port"
        """
        return f"{self.host}:{self.port}"

    def __eq__(self, other: Any) -> bool:
        """Compare if 2 socket addresses are equal."""
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.address == other.address
