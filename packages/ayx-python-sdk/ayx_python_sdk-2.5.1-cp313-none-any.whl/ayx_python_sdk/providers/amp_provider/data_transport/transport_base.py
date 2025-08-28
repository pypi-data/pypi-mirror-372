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
"""
Transport implementation.

Transports provide the functionality for data management and IO.
An implementation should provide an independant way to receive, parse,
serialize, and send data to another service.
"""
from abc import ABC, abstractmethod


class TransportBase(ABC):
    """Transport Manager for the tool."""

    @abstractmethod
    def send_record(self) -> None:
        """Push data to destination."""
        raise NotImplementedError()

    @abstractmethod
    def receive_record(self) -> None:
        """Pull data from source."""
        raise NotImplementedError()
