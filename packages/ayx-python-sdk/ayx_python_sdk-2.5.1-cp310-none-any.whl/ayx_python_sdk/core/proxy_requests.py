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

"""Utility module for proxy authentication and configuration."""
from typing import TYPE_CHECKING

import ayx_python_sdk.core.constants as core_const

from pypac import PACSession

from requests.auth import HTTPProxyAuth

if TYPE_CHECKING:
    from ayx_python_sdk.core import ProviderBase


def create_proxied_session(
    tool_provider: "ProviderBase", use_engine_credentials: bool = True
) -> PACSession:
    """
    Create and return a `requests` session for an environment using a proxy.

    `PACSession` will apply any settings found for PAC on the system. If `use_engine_credentials`
    is `False` you must apply your own credentials to the returned session.
    """
    session = PACSession()
    proxy_conf: dict = tool_provider.environment.proxy_configuration
    # PAC may be used without authentication required, check engine for auth requirement or defer to user for credentials
    if (
        use_engine_credentials
        and proxy_conf.get(core_const.AYX_PROXY_CRED_REQ_KEY, "false") == "true"
    ):
        creds = (
            proxy_conf[core_const.AYX_PROXY_USERNAME_KEY],
            tool_provider.io.decrypt_password(
                proxy_conf[core_const.AYX_PROXY_PASSWORD_KEY]
            ),
        )
        session.proxy_auth = HTTPProxyAuth(*creds)
    return session
