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
"""Conversion methods for AMP Provider classes."""
from datetime import date, datetime, timedelta

from ayx_python_sdk.providers.amp_provider.amp_provider_v2 import AMPProviderV2

import deprecation

from pyarrow import Date32Scalar, int32


# Alteryx Epoch is based closely on Excel's, not UNIX
ALTERYX_DATE32_EPOCH = datetime(1900, 1, 1, 0, 0)


@deprecation.deprecated(
    deprecated_in="2.1.1",
    details="This function is no more necessary since version 2022.2 of Designer",
)  # type: ignore
def arrow_scalar_date32_to_py(
    provider: AMPProviderV2, arrow_date: Date32Scalar
) -> date:
    """
    Convert a Arrow Date32Scalar to a Python datetime object.

    Parameters
    ----------
    provider
        AMPProviderV2 context, necessary for Designer version
    arrow_date
        An Arrow date represented as days since Epoch.

    Returns
    -------
    date
        The converted date value.
    """
    if provider.environment.designer_version < "2022.2":
        return (
            ALTERYX_DATE32_EPOCH + timedelta(arrow_date.cast(int32()).as_py() - 2)
        ).date()
    else:
        return arrow_date.as_py()
