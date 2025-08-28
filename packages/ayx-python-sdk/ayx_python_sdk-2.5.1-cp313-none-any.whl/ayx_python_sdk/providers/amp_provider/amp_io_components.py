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
"""AMP Provider: Proxy class for SDK IO (input/output)."""
import asyncio
import logging
import time
from asyncio.queues import QueueEmpty
from collections import namedtuple
from typing import Any, Callable, Dict, Optional, TYPE_CHECKING

import ayx_python_sdk.providers.amp_provider.grpc_helpers.control_msgs as ctrl_msg
import ayx_python_sdk.providers.amp_provider.grpc_helpers.dcme_msgs as dcm_msg
from ayx_python_sdk.core.exceptions import DcmEException
from ayx_python_sdk.providers.amp_provider.data_transport.amp_transport import (
    AmpStreamTransport,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.output_message_data_pb2 import (
    OutputMessagePriorityFlags,
)
from ayx_python_sdk.providers.amp_provider.resources.generated.sdk_tool_service_v2_pb2 import (
    RecordTransferOut,
)

import deprecation

if TYPE_CHECKING:
    import datetime as dt  # noqa: F401
    from ayx_python_sdk.providers.amp_provider.resources.generated.sdk_tool_service_v2_pb2 import (
        ControlIn,
        ControlOut,
        RecordTransferIn,  # noqa: F401
    )
    from pyarrow import Schema  # noqa: F401


logger = logging.getLogger()
Anchor = namedtuple("Anchor", ["name", "connection"])


class StreamIOBuffer:
    """Defines buffers for RecordTransfer transactions, and provides functions for using them."""

    pending_writes = asyncio.Queue()  # type: ignore
    completed_streams = asyncio.Queue()  # type: ignore
    transport = AmpStreamTransport()

    def receive_chunk(self, msg: "RecordTransferIn") -> None:
        """Receive a RecordIn message containing a chunk or full arrows data stream."""
        completed_record = self.transport.receive_record(msg)

        if completed_record:
            self.completed_streams.put_nowait(
                {
                    "record_batch": completed_record,
                    "anchor": Anchor(
                        msg.incoming_records.anchor_name,
                        msg.incoming_records.connection_name,
                    ),
                }
            )

    def get_stream_msgs(self, record: Dict) -> "RecordTransferOut":  # noqa: D102
        """
        Yield n RecordOut messages with n arrow stream chunks and terminator.

        Where:
        - n is the set chunk size in AmpStreamTransport
        - terminator is `end_of_chunk` in RecordOut.OutgoingRecords
        """
        yield from self.transport.send_record(record["data"], record["anchor_name"])

    def push_record(self, record: dict) -> None:
        """Push a arrows RecordBatch or Table to the write queue."""
        self.pending_writes.put_nowait(record)

    def write_to_buffer(self, name: str, payload: object) -> None:  # noqa: D102
        logger.debug("plugin called write for %s", name)
        try:
            self.push_record(
                {"anchor_name": name, "data": payload, "write_type": "outgoing_records"}
            )
        except Exception as e:
            logger.debug(repr(e))

    async def flush(self) -> None:
        """
        Flush queues in the safest order we can.

        Wait until all streams are received from client, ensuring we call `on_record_batch` for all sent.
        Handle any resulting writes from `on_record_batch` or other methods writing records.
        """
        await self.completed_streams.join()
        await self.pending_writes.join()

    async def dump_queues(self) -> None:
        """Dump any remaining items from the queue. NOT atomic, and is destructive."""
        for q in (self.completed_streams, self.pending_writes):
            try:
                q.get_nowait()
                q.task_done()
            except QueueEmpty:
                logger.debug("Emptied %s", repr(q))
            except Exception as e:
                logger.error(
                    "Error occured while dumping ControlIO buffers! \n %s \n %s",
                    repr(q),
                    repr(e),
                )
                raise e

    def push_close_anchor_msg(self, name: str) -> None:
        """Send ControlOut with CloseOutgoingAnchor."""
        msg = RecordTransferOut()
        msg.close_outgoing_anchor.name = name
        self.push_record({"message": msg, "write_type": "close_outgoing_anchor"})


class ControlIOBuffer:
    """Component Class that wraps all Control IO for the server."""

    # Ignoring type as these are always fresh inits
    ctrl_in_callback = asyncio.Queue()  # type: ignore
    ctrl_out = asyncio.Queue()  # type: ignore
    ctrl_driver_actions = asyncio.Queue()  # type: ignore
    ctrl_user_callback_actions = asyncio.Queue()  # type: ignore
    awaiting_response: Dict[str, Callable] = {}
    blocking_awaiting_response: Dict[str, Any] = {}

    def push_ctrl_out(
        self, msg: "ControlOut", callback_fn: Optional["Callable"] = None
    ) -> None:
        """Push ControlOut to the write queue, notifying server it has something to send."""
        if callback_fn:
            self.awaiting_response[msg.msg_id] = callback_fn
        self.ctrl_out.put_nowait(msg)

    async def flush(self) -> None:
        """
        Shutdown in the safest order possible.

        Let workers empty the control out queue to send any remaining processing needs.
        Wait for any responses to be handled.
        Let workers empty and handle any responses from the client from ctrl_out queue flush.
        Let workers finish any pending actions resulting from the above.
        """
        # Loop until any outstanding callback responses are handled.
        while len(self.awaiting_response) > 0:
            # While we have any requests waiting for a response,
            # send pending requests, execute any current or resulting callbacks
            await self.ctrl_out.join()
            await asyncio.sleep(0)
            await self.ctrl_in_callback.join()
            await self.ctrl_driver_actions.join()
            # loop again if we generated any new awaits
            # otherwise, "done" with this set of ops

    async def dump_queues(self) -> None:
        """Dump remaining items in all queues. NOT atomic, and destructive."""
        for q in (self.ctrl_in_callback, self.ctrl_out, self.ctrl_driver_actions):
            try:
                q.get_nowait()
                q.task_done()
            except QueueEmpty:
                logger.debug("Emptied %s", repr(q))
            except Exception as e:
                logger.error(
                    "Error occured while dumping ControlIO buffers! \n %s \n %s",
                    repr(q),
                    repr(e),
                )
                raise e

    def push_driver_callback(
        self, driver_fn: Callable, *args: tuple, **kwargs: dict
    ) -> asyncio.Event:
        """Push a driver function and parameters. For callables that do not require a client response as an argument."""
        logger.debug(f"pushing callback {driver_fn}")
        event_cb_complete = asyncio.Event()
        action = {
            "driver_fn": driver_fn,
            "args": args,
            "kwargs": kwargs,
            "event_cb_complete": event_cb_complete,
        }
        self.ctrl_driver_actions.put_nowait(action)
        return event_cb_complete

    def push_callback_action(self, msg: "ControlIn") -> None:
        """Place the response message and assigned callback on the action queue."""
        logging.debug("Received callback response, pushing compute...")
        prop_key = msg.WhichOneof("payload")
        if prop_key == "dcm_e_response":
            try:
                resp_msg = dcm_msg.handle_response(msg.dcm_e_response)
            except DcmEException as e:
                logger.error(f"DCME raised exception {repr(e)}")
                raise e
        else:
            resp_msg = getattr(msg, prop_key)
        try:
            action_item = {
                "response_msg": resp_msg,
                "callback_fn": self.awaiting_response.pop(msg.msg_id),
            }
            self.ctrl_user_callback_actions.put_nowait(action_item)
        except KeyError as e:
            logger.error(f"CONTROLIO received msg with invalid ID! \n {repr(e)}")
            raise e

    def error_with_priority(
        self, priority: int, error_msg: str, *args: Any
    ) -> None:  # noqa: D102
        if args:
            msg = ctrl_msg.new_ctrl_out_error_msg(error_msg.format(*args), priority)
        else:
            msg = ctrl_msg.new_ctrl_out_error_msg(error_msg, priority)
        self.push_ctrl_out(msg)

    def warn_with_priority(
        self, priority: int, warn_msg: str, *args: Any
    ) -> None:  # noqa: D102
        if args:
            msg = ctrl_msg.new_ctrl_out_warn_msg(warn_msg.format(*args), priority)
        else:
            msg = ctrl_msg.new_ctrl_out_warn_msg(warn_msg, priority)
        self.push_ctrl_out(msg)

    def info_with_priority(
        self, priority: int, info_msg: str, *args: Any
    ) -> None:  # noqa: D102
        if args:
            msg = ctrl_msg.new_ctrl_out_info_msg(info_msg.format(*args), priority)
        else:
            msg = ctrl_msg.new_ctrl_out_info_msg(info_msg, priority)
        self.push_ctrl_out(msg)

    def error(self, error_msg: str, *args: Any) -> None:  # noqa: D102
        self.error_with_priority(OutputMessagePriorityFlags.OMPF_None, error_msg, *args)

    def warn(self, warn_msg: str, *args: Any) -> None:  # noqa: D102
        self.warn_with_priority(OutputMessagePriorityFlags.OMPF_None, warn_msg, *args)

    def info(self, info_str: str, *args: Any) -> None:  # noqa: D102
        self.info_with_priority(OutputMessagePriorityFlags.OMPF_None, info_str, *args)

    @deprecation.deprecated(
        deprecated_in="1.0.2",
        details="Use functions of provider's dcm property instead",
    )  # type: ignore
    def decrypt_password(self, encrypted_pass: str) -> str:
        """Decrypt the passed value and return readable."""
        # Need to resolve whether or not this is a different call since latest DCM changes.
        try:
            logger.debug("Creating password message...")
            msg = ctrl_msg.new_ctrl_out_decrypt_msg(encrypted_pass)
            self.blocking_awaiting_response[msg.msg_id] = None
            self.push_ctrl_out(msg)
            logger.debug("Waiting for response from client...")
            while self.blocking_awaiting_response[msg.msg_id] is None:
                # Wait for a response. An event may be cleaner looking. Hint for hardening time.
                time.sleep(0)
            result = self.blocking_awaiting_response.pop(msg.msg_id)
            return result.password
        except Exception as e:
            logger.error(repr(e))
            raise e

    def translate_msg_use_callback(
        self, source_str: str, interp_args: list, callback_fn: Callable
    ) -> None:
        """
        Push the msg to the write queue, and assign a reference id for the passed callback.

        DOES NOT BLOCK, and only guarantees the callback will be run before plugin shutdown.
        """
        try:
            logger.debug("Creating Translate Message...")
            msg = ctrl_msg.new_ctrl_out_translate_msg(source_str, *interp_args)
            logger.debug("Callback Assigned, pushing out msg")
            self.push_ctrl_out(msg, callback_fn)
        except Exception as e:
            logger.debug(repr(e))

    def translate_msg(self, source_str: str, *interp_args: list) -> str:
        """Push the msg to the write queue, and block until response."""
        try:
            logger.debug("Creating Translate Message...")
            msg = ctrl_msg.new_ctrl_out_translate_msg(source_str, *interp_args)
            self.blocking_awaiting_response[msg.msg_id] = None
            self.push_ctrl_out(msg)
            logger.debug("Waiting for response from client...")
            while self.blocking_awaiting_response[msg.msg_id] is None:
                # Wait for a response. An event may be cleaner looking. Hint for hardening time.
                time.sleep(0)
            result = self.blocking_awaiting_response.pop(msg.msg_id)
            return result.translated_message
        except Exception as e:
            logger.error(repr(e))
            raise e

    def update_progress(self, progress: float) -> None:
        """Push the msg to the write queue, and block until response."""
        try:
            logger.debug("Creating UpdateProgress Message...")
            msg = ctrl_msg.new_ctrl_out_update_progress_msg(progress)
            self.push_ctrl_out(msg)
        except Exception as e:
            logger.error(repr(e))
            raise e

    def get_connection(
        self, connection_id: str, callback_fn: Callable
    ) -> None:  # noqa: D102
        msg = dcm_msg.get_connection_msg(connection_id)
        self.push_ctrl_out(msg, callback_fn)

    def get_write_lock(
        self,
        connection_id: str,
        role: str,
        secret_type: str,
        expires_in: Optional["dt.datetime"],
        callback_fn: Callable,
    ) -> None:  # noqa: D102
        msg = dcm_msg.get_write_lock_msg(connection_id, role, secret_type, expires_in)
        self.push_ctrl_out(msg, callback_fn)

    def free_write_lock(
        self,
        connection_id: str,
        role: str,
        secret_type: str,
        lock_id: str,
        callback_fn: Optional[Callable] = None,
    ) -> None:  # noqa: D102
        msg = dcm_msg.free_write_lock_msg(connection_id, role, secret_type, lock_id)
        self.push_ctrl_out(msg, callback_fn)

    def update_connection_secret(
        self,
        connection_id: str,
        role: str,
        secret_type: str,
        value: str,
        expires_on: Optional["dt.datetime"],
        parameters: Optional[Dict[str, str]],
        lock_id: str,
        callback_fn: Optional[Callable] = None,
    ) -> None:  # noqa: D102
        msg = dcm_msg.update_connection_secret_msg(
            connection_id, lock_id, role, secret_type, value, expires_on, parameters
        )
        self.push_ctrl_out(msg, callback_fn)

    def get_lock_and_update_secret(
        self,
        connection_id: str,
        role: str,
        secret_type: str,
        value: str,
        expires_on: Optional["dt.datetime"],
        parameters: Optional[Dict[str, str]],
        on_complete: Optional[Callable] = None,
    ) -> None:
        """Set up a callback chain to request a lock, update a secret, and then free the lock."""
        common_args = (connection_id, role, secret_type)

        secret_lock_id = ""

        def _free_lock() -> None:
            nonlocal secret_lock_id

            self.free_write_lock(
                connection_id,
                role,
                secret_type,
                secret_lock_id,
                callback_fn=on_complete,
            )

        def _update_with_lock(resp: dict) -> None:
            nonlocal secret_lock_id
            secret_lock_id = resp["secretLockId"]

            self.update_connection_secret(
                connection_id,
                role,
                secret_type,
                value,
                expires_on,
                parameters,
                secret_lock_id,
                callback_fn=_free_lock,
            )

        self.get_write_lock(*common_args, None, _update_with_lock)
