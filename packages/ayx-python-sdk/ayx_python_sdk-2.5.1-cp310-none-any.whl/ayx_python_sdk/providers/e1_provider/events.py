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
"""Observable event definitions."""
from enum import Enum


class ConnectionEvents(Enum):
    """Events for connection objects."""

    CONNECTION_INITIALIZED = "connection_initialized"
    RECORD_RECEIVED = "record_received"
    PROGRESS_UPDATE = "progress_update"
    CONNECTION_CLOSED = "connection_closed"


class PluginEvents:
    """Events for plugin objects."""

    PLUGIN_INITIALIZED = "plugin_initialized"
    PI_INIT = "pi_init"
    INCOMING_CONNECTION_ADDED = "pi_add_incoming_connection"
    OUTGOING_CONNECTION_ADDED = "pi_add_outgoing_connection"
    PI_CLOSE = "pi_close"
    PI_PUSH_ALL_RECORDS = "pi_push_all_records"
    PLUGIN_FAILURE = "plugin_failure"
