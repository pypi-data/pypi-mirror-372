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
import asyncio
import logging

from ayx_python_sdk.core.constants import Anchor
from ayx_python_sdk.providers.amp_provider.amp_driver import AMPDriver
from ayx_python_sdk.providers.amp_provider.resources.generated.sdk_tool_service_v2_pb2 import (
    ControlOut,
    RecordTransferOut,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.sdk_tool_service_v2_pb2_grpc import (
    SdkToolV2Servicer,
)


class SdkToolServiceV2(SdkToolV2Servicer):
    """Implementation of the SDK Engine V2 service."""

    logger = logging.getLogger()
    driver = AMPDriver()
    init_data: asyncio.Future = asyncio.Future()
    driver_guard: asyncio.Lock = asyncio.Lock()
    cond_teardown = asyncio.Condition(lock=driver_guard)
    record_teardown = asyncio.Condition(lock=driver_guard)
    curr_driver_fn = None
    ready_for_records: asyncio.Event = asyncio.Event()
    record_batch_received: asyncio.Event = asyncio.Event()

    async def Control(self, request_iterator, context):  # type: ignore  # noqa: N802
        """
        Handle Control messages.

        Initialize plugin on initialize ControlIn, then send any ControlOut messages
        to the client as needed, while monitoring for client responses.
        """
        try:
            # Start read/writes and a worker to handle any callbacks for the driver
            tasks = [
                asyncio.create_task(
                    self._ctrl_read(request_iterator), name="_ctrl_read"
                ),
                asyncio.create_task(self._ctrl_write(context), name="_ctrl_write"),
                asyncio.create_task(
                    self._driver_callback_worker(), name="_driver_callback_worker"
                ),
                asyncio.create_task(
                    self._user_callback_worker(), name="_user_callback_worker"
                ),
            ]

            # Clean up tasks
            async with self.cond_teardown:
                self.logger.debug("Control waiting on teardown notification")
                await self.cond_teardown.wait()
                await asyncio.sleep(0)
                complete_msg = ControlOut()
                complete_msg.confirm_complete.SetInParent()
                self.driver.ctrl_io.ctrl_out.put_nowait(complete_msg)
                await self.driver.ctrl_io.ctrl_out.join()
                self.logger.debug("Control starting teardown")
                await self.driver.ctrl_io.flush()
                for t in tasks:
                    t.cancel()
            self.logger.debug("Control stream waiting for close")
        except asyncio.CancelledError as e:
            self.logger.error("ERROR: Client side disconnected from server.")
            self.logger.error(repr(e))

    async def _ctrl_read(self, request_iterator) -> None:  # type: ignore
        awaits_response = {"translated_message", "decrypted_password", "dcm_e_response"}
        async for request in request_iterator:
            payload = request.WhichOneof("payload")
            if payload == "plugin_initialization_data":  # TODO update this to const
                try:
                    asyncio.create_task(
                        self.driver._initialize_plugin(
                            request, self.ready_for_records, self.record_batch_received
                        )
                    )
                except Exception as e:
                    self.logger.error("%s", repr(e))
            elif payload == "incoming_connection_complete":
                conn_info = request.incoming_connection_complete
                closed_anchor = Anchor(conn_info.anchor_name, conn_info.connection_name)
                self.logger.debug("Pushing incoming connection complete")
                if (
                    not self.record_batch_received.is_set()
                ):  # OOP sends incoming_connection_complete without sending any records
                    self.logger.debug("empty row bug detected")
                    self.record_batch_received.set()
                self.driver.ctrl_io.push_driver_callback(
                    self.driver.incoming_connection_complete_callback, closed_anchor
                )
            elif payload in awaits_response:
                try:
                    if self.driver.ctrl_io.awaiting_response.get(request.msg_id):
                        self.driver.ctrl_io.push_callback_action(request)
                    else:
                        self.driver.ctrl_io.blocking_awaiting_response[
                            request.msg_id
                        ] = getattr(request, payload)
                except Exception as e:
                    self.logger.debug(repr(e))
            elif payload == "notify_complete":
                # Notify the driver to start completion
                # The server assumes that the client is done sending RecordIn messages.
                # Client should have sent any incoming records or otherwise at this point.
                self.driver.ctrl_io.push_driver_callback(
                    self.driver.on_complete_callback
                )

    async def _ctrl_write(self, context) -> None:  # type: ignore
        while True:
            msg = await self.driver.ctrl_io.ctrl_out.get()
            try:
                await context.write(msg)
            except Exception as e:  # catch ExecuteBatchError if any
                self.logger.debug(repr(e))
            self.driver.ctrl_io.ctrl_out.task_done()

    async def _user_callback_worker(self) -> None:
        while True:
            action = await self.driver.ctrl_io.ctrl_user_callback_actions.get()
            loop = asyncio.get_event_loop()
            try:
                fn = action["callback_fn"]
                if action.get("response_msg"):
                    fut = loop.run_in_executor(None, fn, action["response_msg"])
                else:
                    fut = loop.run_in_executor(None, fn)
                await fut
                # Could collect these in order
                if fut.exception():
                    raise fut.exception() or BaseException()
            except Exception as e:
                report_str = (
                    f"Failed while calling {action['callback_fn'].__name__}\n {repr(e)}"
                )
                self.logger.error(report_str)
                self.driver.provider.io.error(report_str)
            finally:
                self.driver.ctrl_io.ctrl_user_callback_actions.task_done()

    async def _driver_callback_worker(self) -> None:
        while True:
            action = await self.driver.ctrl_io.ctrl_driver_actions.get()

            # Make sure we clear any queued user callbacks
            await asyncio.sleep(0)
            await self.driver.ctrl_io.ctrl_user_callback_actions.join()

            is_on_complete = action["driver_fn"] == self.driver.on_complete_callback
            if is_on_complete:
                self.logger.debug("got on_complete, checking if need to requeue")
                self.logger.debug(
                    f"ready for on_complete: {self._ready_for_on_complete()}, record_batch_received.is_set(): {self.record_batch_received.is_set()}"
                )
                if (
                    not self._ready_for_on_complete()
                    or not self.record_batch_received.is_set()
                ):
                    self.logger.debug("requeue on_complete")
                    try:
                        await self._requeue_action(
                            action, self.driver.ctrl_io.ctrl_driver_actions
                        )
                    except Exception as e:
                        self.logger.error(e)
                    continue
                elif self.driver.provider.environment.update_only:
                    async with self.record_teardown:
                        self.record_teardown.notify_all()
                    return
            loop = asyncio.get_running_loop()
            if action["args"]:
                fut = loop.run_in_executor(None, action["driver_fn"], *action["args"])
            else:
                # Other plugin methods have no args
                fut = loop.run_in_executor(None, action["driver_fn"])
            # Handle any generated work from calling method
            while fut.done() is False:
                await asyncio.sleep(0.1)
            action["event_cb_complete"].set()
            if fut.exception():
                #  Driver functions still use an error handling wrapper
                #  So we don't have to log here, just teardown
                async with self.record_teardown:
                    self.record_teardown.notify_all()
                raise fut.exception()  # type: ignore
            if is_on_complete:
                async with self.record_teardown:
                    self.record_teardown.notify_all()
                return

    async def _requeue_action(self, action: dict, queue: asyncio.Queue) -> None:
        #  Put action back on to passed queue.
        await asyncio.sleep(0)
        await queue.put(action)
        queue.task_done()

    def _ready_for_on_complete(self) -> bool:
        pre_complete_actions = self.driver.ctrl_io.ctrl_driver_actions.empty()
        pending_record_batches = self.driver.record_io.completed_streams.empty()
        awaiting_responses = len(self.driver.ctrl_io.awaiting_response) < 1
        return all([pre_complete_actions, pending_record_batches, awaiting_responses])

    async def RecordTransfer(self, request_iterator, context):  # type: ignore  # noqa: N802
        """
        Definition for gRPC RecordTransfer.

        Consumes any data sent by the client, then send any pending RecordTransferOut messages.
        """
        self.logger.debug("Record Transfer stream starting.")
        tasks = [
            asyncio.create_task(
                self._record_read(request_iterator), name="_record_read"
            ),
            asyncio.create_task(self._record_write(context), name="_record_write"),
            asyncio.create_task(
                self._record_driver_actions(), name="_record_driver_actions"
            ),
        ]
        async with self.record_teardown:
            self.logger.debug("Waiting on teardown notification")
            await self.record_teardown.wait()
            await asyncio.sleep(0)
            self.logger.debug("Received teardown notice. Cancelling tasks")
            try:
                for _, anchor in self.driver.provider.outgoing_anchors.items():
                    if (
                        anchor["num_connections"] > 0 or anchor.get("metadata")
                    ) and not self.driver.provider.environment.update_only:
                        rec_out_chunk_end = RecordTransferOut()
                        rec_out_chunk_end.close_outgoing_anchor.name = anchor["name"]
                        self.driver.record_io.pending_writes.put_nowait(
                            {
                                "write_type": "close_outgoing_anchor",
                                "message": rec_out_chunk_end,
                            }
                        )

                await self.driver.record_io.flush()
                for t in tasks:
                    t.cancel()
            except Exception as e:
                self.logger.debug(repr(e))
        async with self.cond_teardown:
            self.cond_teardown.notify_all()
        self.logger.debug("Exiting RecordTransfer...")

    async def _record_read(self, request_iterator) -> None:  # type: ignore
        """Receive any RecordTransferIn messages from the client."""
        async for req in request_iterator:
            payload = req.WhichOneof("payload")
            if payload == "incoming_records":
                self.driver.record_io.receive_chunk(req)

    async def _record_write(self, context) -> None:  # type: ignore
        """Write and send RecordTransferOut.outgoing_records from write queue."""
        while True:
            # If user has written to buffer, send records
            to_write = await self.driver.record_io.pending_writes.get()
            if to_write["write_type"] == "outgoing_records":
                for msg in self.driver.record_io.get_stream_msgs(to_write):
                    await context.write(msg)
            else:
                try:
                    anchor = self.driver.provider.outgoing_anchors[
                        to_write["message"].close_outgoing_anchor.name
                    ]
                    if (
                        anchor["num_connections"] > 0
                        and not anchor.get("metadata", False)
                    ) and not self.driver.provider.environment.update_only:
                        self.logger.debug("Wrote close anchor")
                    await context.write(to_write["message"])
                except Exception as e:
                    self.logger.error("Failed during record_write: %s", repr(e))
            self.driver.record_io.pending_writes.task_done()

    async def _record_driver_actions(self) -> None:
        """Handle events related to receiving or sending batches."""
        while True:
            batch_item = await self.driver.record_io.completed_streams.get()
            self.logger.debug(f"Got a msg from completed_streams queue: {batch_item}")
            await self.ready_for_records.wait()  # wait for plugin_init to finish before calling on_record_batch
            self.driver.ctrl_io.push_driver_callback(
                self.driver.record_batch_received,
                batch_item["record_batch"],
                batch_item["anchor"],
            )
            self.record_batch_received.set()
            self.driver.record_io.completed_streams.task_done()
