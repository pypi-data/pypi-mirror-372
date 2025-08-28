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
"""Tool configuration builder file."""
from typing import Any, Dict

import xmltodict


class ToolConfigBuilder:
    """Builder class for converting the tool configuration XML to and from a dict."""

    @staticmethod
    def to_xml(config_dict: Dict[str, Any]) -> str:
        """
        Convert a tool configuration dictionary to the expected XML formatted string.

        Parameters
        ----------
        config_dict
            The dictionary representation of the tool configuration XML

        Returns
        -------
        str
            Tool configuration unparsed into an XML string
        """
        return xmltodict.unparse(
            {"Configuration": config_dict}, short_empty_elements=True
        )

    @staticmethod
    def from_xml(xml_string: str) -> Dict[str, Any]:
        """
        Convert a tool configuration XML to the expected dictionary.

        Parameters
        ----------
        xml_string
            The tool configuration XML string to be converted into a Python dict

        Returns
        -------
        dict
            The dictionary representation of the passed in XML
        """
        return dict(
            xmltodict.parse(xml_string, strip_whitespace=False)["Configuration"] or {}
        )
