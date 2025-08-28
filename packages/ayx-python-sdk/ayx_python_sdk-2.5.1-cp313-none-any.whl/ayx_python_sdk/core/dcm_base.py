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
"""DCM API base class definition."""
import datetime as dt
from abc import ABC, abstractmethod
from typing import Dict, Optional


class DcmBase(ABC):
    """
    Dcm base class.

    This base class provides API to work with engine's DCM objects .
    """

    @abstractmethod
    def get_connection(self, connection_id: str) -> Dict:
        """
        Retrieve connection information including secrets by connection ID.

        Parameters
        ----------
        connection_id
            string with UUID of connection
        """
        raise NotImplementedError()

    @abstractmethod
    def get_write_lock(
        self,
        connection_id: str,
        role: str,
        secret_type: str,
        expires_in: Optional[dt.datetime],
    ) -> Dict:
        """
        Attempt to acquire an exclusive write lock.

        Parameters
        ----------
        connection_id
            string with UUID of connection
        role
            A role such as ?oauth?
        secret_type
            A secret type such as ?oauth_token?
        expires_in
            (Optional) A DateTime value in which to ask for the lock to be held for in milliseconds.
            Defaults to 0.
        """
        raise NotImplementedError()

    @abstractmethod
    def free_write_lock(
        self, connection_id: str, role: str, secret_type: str, lock_id: str
    ) -> None:
        """
        Free a lock obtained from a previous call to get_write_lock().

        Parameters
        ----------
        connection_id
            string with UUID of connection
        role
            A role such as ?oauth?
        secret_type
            A secret type such as ?oauth_token?
        lock_id
            A lock_id acquired from a previous call to get_write_lock()
        """
        raise NotImplementedError()

    @abstractmethod
    def update_connection_secret(
        self,
        connection_id: str,
        lock_id: str,
        role: str,
        secret_type: str,
        value: str,
        expires_on: Optional[dt.datetime],
        parameters: Optional[Dict[str, str]],
    ) -> Dict:
        """
        Update a single secret for role and secret_type to value as well as the optional expires_on and parameters.

        Parameters
        ----------
        connection_id
            A connection ID
        lock_id
            A lock ID acquired from get_write_lock()
        role
            A role such as ?oauth?
        secret_type
            A secret type such as ?oauth_token?
        value
            The new value to store for the secret
        expires_on
            (Optional) DateTime of expiration of this secret
        parameters
            Dict of parameter values for this secret (this is arbitrary user data stored as JSON)
        """
        raise NotImplementedError()
