# SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Helper module for USD types."""

# Third Party
from pxr import Sdf


class ValidUsdTypes:
    """Helper class to make discovering valid USD types easier.

    This class is not meant to be instantiated (but it can be). It is meant be used in an
    interactive python session to discover valid USD types. An example usage in an `ipython` session
    would look like this

    ```
    import nvidia.srl.usd.types_helper as types_helper
    types_helper.ValidUsdTypes.<tab complete>
    ```

    The attributes in `ValidUsdTypes` are the types listed on the left hand side of the table on
    this page: https://developer.nvidia.com/usd/tutorials
    """

    pass


for attr_name in dir(Sdf.ValueTypeNames):
    attr_val = getattr(Sdf.ValueTypeNames, attr_name)
    if isinstance(attr_val, Sdf.ValueTypeName):
        setattr(ValidUsdTypes, attr_name, attr_val)
