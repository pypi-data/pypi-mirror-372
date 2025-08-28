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
"""Class for running a plugin out of process."""
import asyncio
import os
import sys
import time
from enum import Enum
from pathlib import Path
from typing import AsyncIterable, Callable, List, Optional, TYPE_CHECKING, Tuple

from ayx_python_sdk.providers.amp_provider import (
    AMPInputAnchor,
    AMPInputConnection,
    AMPOutputAnchor,
)
from ayx_python_sdk.providers.amp_provider.builders import OutputAnchorBuilder
from ayx_python_sdk.providers.amp_provider.builders.input_anchor_builder import (
    InputAnchorBuilder,
)
from ayx_python_sdk.providers.amp_provider.data_transport.amp_transport import (
    AmpStreamTransport,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.plugin_initialization_data_pb2 import (
    UpdateMode,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.sdk_tool_service_pb2_grpc import (
    SdkToolStub,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.sdk_tool_service_v2_pb2 import (
    ControlIn,
    RecordTransferIn,
    RecordTransferOut,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.sdk_tool_service_v2_pb2_grpc import (
    SdkToolV2Stub,
)
from ayx_python_sdk.test_harness.process_lifecycle_manager import (
    ProcessLifecycleManager,
)

import grpc

import pyarrow as pa

import typer

import xmltodict


if TYPE_CHECKING:
    from ayx_python_sdk.core import Metadata  # noqa: F401
    import pandas as pd  # noqa: F401


class RunMode(str, Enum):
    """Run mode types."""

    update_only = "update_only"
    full_run = "full"


def _handle_sdk_tool_service_exception(method: Callable) -> Callable:
    def _log_grpc_errors(*args, **kwargs):  # type: ignore
        try:
            return method(*args, **kwargs)
        except grpc.RpcError as e:
            typer.echo("SDK Tool Service failed.")
            typer.echo(f"gRPC Status Code: {e.code()}")
            typer.echo(f"gRPC Details (Stacktrace):\n{e.details()}")
            raise typer.Exit(code=1)

    return _log_grpc_errors


def _parse_config_xml(
    xml_path: Path,
) -> Tuple[List[AMPInputAnchor], List[AMPOutputAnchor]]:
    input_anchors = []
    output_anchors = []
    typer.echo(f"{xml_path}")
    with open(xml_path) as config_xml:
        config_dict = xmltodict.parse(config_xml.read())
        inputs = config_dict["AlteryxJavaScriptPlugin"]["GuiSettings"][
            "InputConnections"
        ]["Connection"]
        outputs = config_dict["AlteryxJavaScriptPlugin"]["GuiSettings"][
            "OutputConnections"
        ]["Connection"]
        if type(inputs) is list:
            for input_anchor in inputs:
                anchor = AMPInputAnchor(
                    name=input_anchor["@Name"],
                    allow_multiple=input_anchor["@AllowMultiple"],
                    optional=input_anchor["@Optional"],
                )
                input_anchors.append(anchor)
        else:
            anchor = AMPInputAnchor(
                name=inputs["@Name"],
                allow_multiple=inputs["@AllowMultiple"],
                optional=inputs["@Optional"],
            )
            input_anchors.append(anchor)

        if type(outputs) is list:
            for output_anchor in outputs:
                anchor = AMPOutputAnchor(
                    name=output_anchor["@Name"],
                    allow_multiple=output_anchor["@AllowMultiple"],
                    optional=output_anchor["@Optional"],
                )
                output_anchors.append(anchor)
        else:
            anchor = AMPOutputAnchor(
                name=outputs["@Name"],
                allow_multiple=outputs["@AllowMultiple"],
                optional=outputs["@Optional"],
            )
            output_anchors.append(anchor)

    return input_anchors, output_anchors


class PluginRunner:
    """Class for running a plugin out of process with test data."""

    def __init__(
        self,
        plugin_entrypoint: Path,
        plugins_package: str,
        tool_name: str,
        input_metadata: List["Metadata"],
        input_data: List["pd.DataFrame"],
        config_xml: Path,
        transport_type: str,
    ) -> None:
        """Construct the plugin runner."""
        self._channel = None
        self._plugin_entrypoint = plugin_entrypoint
        self._plugins_package = plugins_package
        self._tool_name = tool_name
        self._input_metadata = input_metadata
        self._input_data = input_data
        self._transport_type = transport_type
        self._sdk_tool_client: Optional[SdkToolStub] = None
        self._input_anchors, self._output_anchors = _parse_config_xml(config_xml)
        self._control_write_queue: asyncio.Queue[ControlIn] = asyncio.Queue()
        self._control_read_queue: list = []
        self._record_write_queue: asyncio.Queue[RecordTransferIn] = asyncio.Queue()
        self._received_records: List[RecordTransferOut] = []
        self.stream_transport = AmpStreamTransport()
        for i in range(len(self._input_anchors)):
            connection = [
                AMPInputConnection(
                    "Connection" + str(i),
                    metadata=self._input_metadata[i],
                    anchor=self._input_anchors[i],
                )
            ]
            self._input_anchors[i].connections.extend(connection)
        typer.echo(f"{transport_type}")
        if not (len(self._input_data) == len(self._input_metadata)):
            typer.echo(
                f"{len(self._input_data)}\n{self._input_anchors}\n{len(self._input_metadata)}"
            )
            raise Exception(
                "Input datasets, input metadata, and input anchors must match."
            )

    async def run_plugin_v2(self, mode: RunMode) -> None:
        """Run the plugin out of process."""
        with ProcessLifecycleManager(
            [
                sys.executable,
                str(self._plugin_entrypoint.resolve()),
                "start-sdk-tool-service",
                self._plugins_package,
                self._tool_name,
                "--sdk-engine-server-address",
                "localhost:6500",
            ]
        ) as plugin_process:  # noqa: F841
            try:
                self.channel = grpc.aio.insecure_channel(
                    "localhost:6500",
                    options=[
                        ("grpc.max_send_message_length", -1),
                        ("grpc.max_receive_message_length", -1),
                    ],
                )
                await self._wait_for_handshake_v2(plugin_process)
                self.sdk_client_stub = SdkToolV2Stub(self.channel)
            except Exception as e:
                typer.echo(f"Error while running handshake")
                raise e

            # TODO: should return a status and raise if failed
            if mode == RunMode.full_run:
                await self._handle_plugin_runtime()

    async def _wait_for_handshake_v2(
        self, plugin_process: ProcessLifecycleManager, timeout: float = 30.0
    ) -> None:
        """Wait for the initialization handshake to complete."""
        start = time.time()
        await asyncio.wait_for(self.channel.channel_ready(), timeout)
        typer.echo("Channel ready")
        if not plugin_process.process_alive():
            typer.echo(
                f"ERROR: Plugin process died before handshake completed with error."
            )
            raise typer.Exit(code=1)

        if time.time() - start > timeout:
            typer.echo("ERROR: Handshake didn't complete within timeout.")
            raise typer.Exit(code=1)

    @_handle_sdk_tool_service_exception
    def _initialize_plugin_v2_msg(self) -> None:
        """Initialize the plugin with metadata and configuration."""
        dummy_plugin_data = ControlIn()
        dummy_plugin_data.plugin_initialization_data.configXml = "<Configuration />"
        dummy_plugin_data.plugin_initialization_data.incomingAnchors.extend(
            [
                InputAnchorBuilder.to_protobuf(input_anchor)
                for input_anchor in self._input_anchors
            ]
        )
        dummy_plugin_data.plugin_initialization_data.outgoingAnchors.extend(
            [
                OutputAnchorBuilder.to_protobuf(output_anchor)
                for output_anchor in self._output_anchors
            ]
        ),
        engine_constants = {
            "Engine.TempFilePath": os.getcwd(),
            "Engine.WorkflowDirectory": os.getcwd(),
            "Engine.Version": "0.0.0.0",
            "ToolId": "10",
            "AlteryxExecutable": os.getcwd(),
            "ProxyConfiguration": "ProxyRequiresCredentials=false\nProxyCommonUserName=\nProxyCommonPassword=\n",
            "WorkflowRunGuid": "aa163794-e400-4ec5-85dd-a7de71bedb8a",
        }
        for k, v in engine_constants.items():
            dummy_plugin_data.plugin_initialization_data.engineConstants[k] = v
        dummy_plugin_data.plugin_initialization_data.updateMode = UpdateMode.UM_Run
        return dummy_plugin_data

    def _push_input_data_to_queue(self) -> None:
        try:
            for num, anchor in enumerate(self._input_anchors):
                batch = pa.RecordBatch.from_pandas(self._input_data[num])
                stream = self.stream_transport.get_rec_stream(batch)
                try:
                    for chunk, end_of_chunk in self.stream_transport.iter_stream(
                        stream
                    ):
                        msg = RecordTransferIn()
                        msg.incoming_records.anchor_name = anchor.name
                        msg.incoming_records.data = chunk
                        msg.incoming_records.end_of_chunk = end_of_chunk
                        msg.incoming_records.connection_name = anchor.connections[
                            num
                        ].name
                        self._record_write_queue.put_nowait(msg)
                except StopIteration:
                    pass
        except Exception as e:
            typer.echo(f"Exception during push input data {repr(e)}")

    async def record_transfer_producer(
        self,
        event_plugin_ready: "asyncio.Event",
    ) -> "RecordTransferIn":
        """Send records to the plugin, notify client is done sending record data."""
        # wait for plugin init event
        await event_plugin_ready.wait()
        typer.echo("Sending initial recordtransfers")
        while not self._record_write_queue.empty():
            yield await self._record_write_queue.get()
            self._record_write_queue.task_done()
        typer.echo("Sent initial transfers.")
        typer.echo("Notifying plugin to complete")
        self._control_write_queue.put_nowait(self._get_notify_complete_msg())

    async def control_producer(
        self,
        event_notify_complete: "asyncio.Event",
        event_plugin_ready: "asyncio.Event",
    ) -> "ControlIn":
        """Generate initial control messages, then wait for any new msgs to send from the queue."""
        typer.echo("Sending init message")
        yield self._initialize_plugin_v2_msg()
        # await event_plugin_ready.wait()  # Wait for plugin to send back init response
        typer.echo("Init successful, starting control in loop")
        # Start regular producer loop
        while not event_notify_complete.is_set():
            if not self._control_write_queue.empty():
                yield await self._control_write_queue.get()
                # send back any handled control_out messages
                self._control_write_queue.task_done()
                # let the client check on other streams
            await asyncio.sleep(0)

    @_handle_sdk_tool_service_exception
    async def record_transfer_consumer(
        self, resp_iterator: AsyncIterable[RecordTransferOut]
    ) -> None:
        """Receive and process RecordTransferOut messages from the server."""
        # check for notify_complete AFTER handling any remaining pending record_out respones
        async for resp in resp_iterator:
            typer.echo("Response received on record consumer stream")
            if resp.WhichOneof("payload") == "outgoing_records":
                typer.echo("Consumer received record msg.")
                record_chunk = resp.outgoing_records
                try:
                    completed_stream = self.stream_transport.receive_record(
                        record_chunk
                    )
                    if completed_stream:
                        self._received_records.append(completed_stream)
                except Exception as e:
                    typer.echo(f"{repr(e)}")

    async def control_consumer(
        self,
        event_notify_complete: "asyncio.Event",
        event_plugin_ready: "asyncio.Event",
        resp_iterator: AsyncIterable["RecordTransferOut"],
    ) -> None:
        """Receives and handles Control msg responses from the server."""
        async for resp in resp_iterator:
            oneof = resp.WhichOneof("payload")
            typer.echo(f"control consumer received oneof {oneof}")
            if oneof == "translate_message":
                # Return translated message, for now just flip it back
                msg = ControlIn()
                fake_translated = (
                    f"'Translated msg': {resp.translate_message.unlocalized_string}"
                )
                msg.translated_message.translated_message = fake_translated
                msg.msg_id = resp.msg_id
                typer.echo(
                    f"Sending translated message response to control write queue..."
                )
                self._control_write_queue.put_nowait(msg)
            elif resp.WhichOneof("payload") == "confirm_complete":
                typer.echo("Received plugin complete confirmation from SDK tool")
                # Set plugin complete, asyncio.gather should let data streams finish work.
                event_notify_complete.set()
            elif oneof == "output_message":
                if (
                    event_plugin_ready.is_set() is False
                    and "Plugin Initialized" in resp.output_message.message
                ):
                    typer.echo("Recieved SDK PLUGIN init confirmation")
                    event_plugin_ready.set()
                typer.echo(
                    f"Received control out from server. \n {resp.output_message.message}"
                )

    def _get_notify_complete_msg(self) -> "ControlIn":
        """Create notify complete msg."""
        ctrl_msg = ControlIn()
        ctrl_msg.notify_complete.SetInParent()
        return ctrl_msg

    @_handle_sdk_tool_service_exception
    async def _handle_plugin_runtime(self) -> None:
        """Send/receive all of the record packets to/from the plugin."""
        typer.echo("Starting plugin runtime")
        if self.sdk_client_stub is None:
            typer.echo("Stub not set")
            raise ValueError("SDK Tool Client must be set.")
        event_notify_plugin_complete = asyncio.Event()
        event_plugin_ready = asyncio.Event()
        typer.echo("Setting input data...")
        try:
            self._push_input_data_to_queue()
        except Exception as e:
            typer.echo("Exception during setting input data")
            raise e
        typer.echo("Setting Producers")
        record_transfer_responses = self.sdk_client_stub.RecordTransfer(
            self.record_transfer_producer(event_plugin_ready)
        )
        control_responses = self.sdk_client_stub.Control(
            self.control_producer(event_notify_plugin_complete, event_plugin_ready)
        )
        # Separate tasks to thread to let control listen for server msgs
        typer.echo("Setting Consumers")
        _record_consumer = self.record_transfer_consumer(record_transfer_responses)
        _ctrl_consumer = self.control_consumer(
            event_notify_plugin_complete,
            event_plugin_ready,
            control_responses,
        )
        # TODO: Add task status returns
        typer.echo("Gathering...")
        tasks = await asyncio.gather(_record_consumer, _ctrl_consumer)
        typer.echo(tasks)
        typer.echo("Received records:")
        for rec in self._received_records:
            typer.echo(rec)
