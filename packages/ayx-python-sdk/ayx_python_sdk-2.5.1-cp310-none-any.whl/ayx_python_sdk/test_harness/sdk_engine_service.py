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
"""Test harness implementation of the SDK Engine service."""
from ayx_python_sdk.providers.amp_provider.grpc_util import SocketAddress
from ayx_python_sdk.providers.amp_provider.repositories.test_harness_state_repository import (
    TestHarnessStateRepository,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.output_message_data_pb2 import (
    OutputMessageTypes,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.password_data_pb2 import (
    PasswordData,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.sdk_engine_service_pb2_grpc import (
    SdkEngineServicer,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.translate_message_data_pb2 import (
    TranslatedMessage,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.transport_pb2 import (
    Empty,
    ReturnStatus,
)

import typer


class SdkEngineService(SdkEngineServicer):
    """Implementation of the SDK Engine service for the test harness."""

    def ConfirmSdkEngineServiceConnection(self, request, context):  # type: ignore  # noqa: N802
        """Confirm the connection with this server."""
        typer.echo(
            f"SDK ENGINE SERVICE: ConfirmSdkEngineServiceConnection called with request:\n{request}"
        )

        TestHarnessStateRepository().save_handshake_completed_status(True)

        TestHarnessStateRepository().save_sdk_tool_server_address(
            SocketAddress.from_address_str(request.sdk_tool_server_address)
        )

        return ReturnStatus(success=True, message="Connection successful.")

    def PushOutgoingMetadata(self, request, context):  # type: ignore  # noqa: N802
        """Send any outgoing metadata from Sdk Plugin to SDK Engine Server."""
        typer.echo(
            f"SDK ENGINE SERVICE: PushOutgoingMetadata called with request:\n{request}"
        )

        TestHarnessStateRepository().save_metadata(
            request.output_anchor_name, request.metadata
        )

        return ReturnStatus(success=True, message="Output anchor and metadata saved.")

    def PushOutgoingRecordPacket(self, request, context):  # type: ignore # noqa: N802
        """Push any record packets from SDK Plugin to SDK Engine Server."""
        typer.echo(
            f"SDK ENGINE SERVICE: PushOutgoingRecordPacket called with request:\n{request}"
        )

        TestHarnessStateRepository().save_record_packet(
            request.anchor_name, request.record_packet
        )
        return ReturnStatus(success=True, message="Record packet saved.")

    def TranslateMessage(self, request, context):  # type: ignore # noqa: N802
        """Translate message into the correct locale, passing in any interpolation items."""
        typer.echo(
            f"SDK ENGINE SERVICE: TranslateMessage called with request:\n{request}"
        )

        return TranslatedMessage(translated_message=request.unlocalized_string)

    def OutputMessage(self, request, context):  # type: ignore # noqa: N802
        """Push output message."""
        prefix = {
            OutputMessageTypes.OMT_Info: "INFO",
            OutputMessageTypes.OMT_Warning: "WARNING",
            OutputMessageTypes.OMT_Error: "ERROR",
            OutputMessageTypes.OMT_UpdateOutputConfigXml: "XML_UPDATE",
        }[request.message_type]

        typer.echo("SDK ENGINE SERVICE: Output message received from plugin")
        typer.echo(f"{prefix}: {request.message}\n")

        return Empty()

    def DecryptPassword(self, request, context):  # type: ignore # noqa: N802
        """Decrypt a passsword."""
        typer.echo(
            f"SDK ENGINE SERVICE: DecryptPassword {request.password} received from plugin"
        )
        return PasswordData(password=request.password + "_decrypted")
