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
"""E1 Provider: Proxy class for DCM API."""
import datetime as dt
from typing import Dict, Optional

from ayx_python_sdk.core import DcmBase
from ayx_python_sdk.core.doc_utilities import inherit_docs


@inherit_docs
class E1ProviderDCM(DcmBase):
    """Class that wraps  DCM API work."""

    def get_connection(self, connection_id: str) -> Dict:  # noqa: D102
        raise NotImplementedError()

    def get_write_lock(
        self,
        connection_id: str,
        role: str,
        secret_type: str,
        expires_in: Optional[dt.datetime],
    ) -> Dict:  # noqa: D102
        raise NotImplementedError()

    def free_write_lock(
        self, connection_id: str, role: str, secret_type: str, lock_id: str
    ) -> None:  # noqa: D102
        raise NotImplementedError()

    def update_connection_secret(
        self,
        connection_id: str,
        lock_id: str,
        role: str,
        secret_type: str,
        value: str,
        expires_on: Optional[dt.datetime],
        parameters: Optional[Dict[str, str]],
    ) -> Dict:  # noqa: D102
        raise NotImplementedError()
