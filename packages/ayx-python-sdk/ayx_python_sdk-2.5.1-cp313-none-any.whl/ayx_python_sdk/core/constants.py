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
"""Constant definitions."""
from collections import namedtuple

AWAIT_TIMEOUT = 5.0

NULL_VALUE_PLACEHOLDER = "AYX_SDK_NULL_VALUE_PLACEHOLDER"

AYX_PROXY_USERNAME_KEY = "ProxyCommonUserName"
AYX_PROXY_PASSWORD_KEY = "ProxyCommonPassword"
AYX_PROXY_CRED_REQ_KEY = "ProxyRequiresCredentials"

Anchor = namedtuple("Anchor", ["name", "connection"])
