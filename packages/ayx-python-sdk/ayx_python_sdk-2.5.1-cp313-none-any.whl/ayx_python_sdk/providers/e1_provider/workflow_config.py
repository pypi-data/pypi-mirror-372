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
"""Alteryx tool workflow configuration definition."""
from collections import UserDict
from copy import deepcopy

import xmltodict


class WorkflowConfiguration(UserDict):
    """Workflow configuration."""

    __slots__ = ["data", "original_data"]

    def __init__(self, config_str: str):
        """Initialize a workflow configuration."""
        self.data = (
            xmltodict.parse(config_str, strip_whitespace=False)["Configuration"] or {}
        )
        self.original_data = deepcopy(self.data)
