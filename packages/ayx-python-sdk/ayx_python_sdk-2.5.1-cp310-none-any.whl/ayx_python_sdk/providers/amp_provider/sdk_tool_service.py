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
"""SDK Engine Service grpc class."""
import logging
import traceback
from typing import Any, Callable

from ayx_python_sdk.providers.amp_provider import AMPDriver, AMPProvider
from ayx_python_sdk.providers.amp_provider.repositories import (
    EnvironmentRepository,
    GrpcRepository,
    InputAnchorRepository,
    InputMetadataRepository,
    InputRecordPacketRepository,
    OutputAnchorRepository,
    PluginClassRepository,
    ToolConfigRepository,
    clear_repositories,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.sdk_tool_service_pb2_grpc import (
    SdkToolServicer,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.transport_pb2 import (
    ReturnStatus,
)

import grpc


logger = logging.getLogger()


def _handle_service_exception(method: Callable) -> Callable:
    def _handle_exception(obj, request, context) -> Any:  # type: ignore
        try:
            return method(obj, request, context)
        except Exception:
            traceback_str = traceback.format_exc()
            logger.exception(traceback_str)
            context.set_details(traceback_str)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.abort(code=grpc.StatusCode.INTERNAL, details=traceback_str)

    return _handle_exception


class SdkToolService(SdkToolServicer):
    """SDK Tool Service GRPC overrides."""

    @_handle_service_exception
    def ConfirmSdkToolServiceConnection(self, request, context):  # type: ignore # noqa: N802
        """Confirm healthy connection.

        Parameters
        ----------
        request: Empty
            The incoming gRPC request - should be empty for this method

        context: grpc.ServicerContext
            Service-level context for this gRPC service
        """
        logger.debug("ConfirmSdkToolServiceConnection called.")
        status = ReturnStatus(message=f"Connection successful!", success=True)
        return status

    @_handle_service_exception
    def InitializeSdkPlugin(self, request, context):  # type: ignore # noqa: N802
        """
        Initialize SDK Plugin with config, anchors, and connections.

        Parameters
        ----------
        request: PluginInitializationData
            The incoming gRPC request - should contain tool config, engine constants, list of incoming and outgoing anchors, and a boolean updataMode.

        context: grpc.ServicerContext
            Service-level context for this gRPC service

        """
        logger.debug("InitializeSdkPlugin called.")
        AMPDriver().clear_state()
        clear_repositories(exclude={GrpcRepository(), PluginClassRepository()})

        ToolConfigRepository().save_xml_tool_config(request.configXml)
        EnvironmentRepository().save_engine_constants(dict(request.engineConstants))
        EnvironmentRepository().save_update_mode(request.updateMode)

        for input_anchor in request.incomingAnchors:
            logger.debug("Saving input anchor: \n%s\n", input_anchor)
            InputAnchorRepository().save_grpc_anchor(input_anchor)

        for output_anchor in request.outgoingAnchors:
            logger.debug("Saving output anchor: \n%s\n", output_anchor)
            OutputAnchorRepository().save_grpc_anchor(output_anchor)

        amp_provider = AMPProvider()
        sdk_plugin = PluginClassRepository().get_plugin_class()(amp_provider)
        AMPDriver().plugin = sdk_plugin

        for anchor in request.incomingAnchors:
            for connection in anchor.connections:
                logger.debug(
                    "Driving metadata for input anchor %s and connection %s.",
                    anchor.name,
                    connection.name,
                )
                AMPDriver().metadata_received(anchor.name, connection.name)

        status = ReturnStatus(message=f"Initialization successful!", success=True)
        return status

    @_handle_service_exception
    def PushIncomingRecordPacket(self, request, context):  # type: ignore # noqa: N802
        """
        Push a record packet to the plugin.

        Parameters
        ----------
        request: IncomingRecordPacketPush
            The incoming gRPC request - should contain an anchor name, connection name, and the record packet to send.

        context: grpc.ServicerContext
            Service-level context for this gRPC service.
        """
        logger.debug("PushIncomingRecordPacket called.")
        logger.debug(
            "Packet received on anchor %s and connection %s.",
            request.anchor_name,
            request.connection_name,
        )
        record_packet_metadata = InputMetadataRepository().get_metadata(
            request.anchor_name, request.connection_name
        )
        InputRecordPacketRepository().save_grpc_record_packet(
            anchor_name=request.anchor_name,
            connection_name=request.connection_name,
            grpc_record_packet=request.record_packet,
            metadata=record_packet_metadata,
        )
        logger.debug(
            "Driving record packet to plugin on anchor %s and connection %s.",
            request.anchor_name,
            request.connection_name,
        )
        AMPDriver().record_packet_received(
            anchor_name=request.anchor_name,
            connection_name=request.connection_name,
        )
        status = ReturnStatus(message="Record packet recieved!", success=True)
        return status

    @_handle_service_exception
    def NotifyIncomingConnectionComplete(self, request, context):  # type: ignore # noqa: N802
        """
        Notify the plugin that a connection has closed.

        Parameters
        ----------
        request: IncomingConnectionComplete
            The incoming gRPC request - should contain an anchor name and connection name.

        context: grpc.ServicerContext
            Service-level context for this gRPC service
        """
        logger.debug("NotifyIncomingConnectionComplete called.")

        AMPDriver().connection_closed_callback(
            request.anchor_name, request.connection_name
        )
        logger.debug(
            "Connection closed for anchor %s, connection %s",
            request.anchor_name,
            request.connection_name,
        )
        status = ReturnStatus(
            message=f"Connection {request.connection_name} closed!", success=True
        )
        return status

    @_handle_service_exception
    def NotifyPluginComplete(self, request, context):  # type: ignore # noqa: N802
        """
        Notify the plugin that the on_complete method should be called.

        Parameters
        ----------
        request: Empty
            The incoming gRPC request - should be empty for this method

        context: grpc.ServicerContext
            Service-level context for this gRPC service
        """
        logger.debug("NotifyPluginComplete Called")
        AMPDriver().complete_callback()
        status = ReturnStatus(message=f"Plugin process complete!", success=True)
        return status
