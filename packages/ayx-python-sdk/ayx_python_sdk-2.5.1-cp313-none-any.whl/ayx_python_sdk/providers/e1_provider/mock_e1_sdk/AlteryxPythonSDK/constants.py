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
"""SDK constants."""


class Status:
    """Status constants."""

    update_output_config_xml = 0


class EngineMessageType:
    """Engine output message types."""

    error = 100
    warning = 101
    info = 102


class FieldType:
    """SDK field types."""

    blob = "blob"
    byte = "byte"
    int16 = "int16"
    int32 = "int32"
    int64 = "int64"
    float = "float"
    double = "double"
    date = "date"
    time = "time"
    datetime = "datetime"
    bool = "bool"
    string = "string"
    v_string = "v_string"
    v_wstring = "v_wstring"
    wstring = "wstring"
    fixeddecimal = "fixeddecimal"
    spatialobj = "spatialobj"
