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
"""Get the E1 package."""
import sys
from pathlib import Path


def cache_e1_sdk_import() -> None:
    """
    Cache the import for the E1 SDK.

    This is necessary in order to remove the dependency on the
    AlteryxPythonSDK package.
    """
    try:
        import AlteryxPythonSDK  # noqa: F401
    except ModuleNotFoundError:
        mock_e1_sdk_package_dir = Path(__file__).parent / "mock_e1_sdk"
        sys.path.append(str(mock_e1_sdk_package_dir))
        import AlteryxPythonSDK  # noqa: F401
