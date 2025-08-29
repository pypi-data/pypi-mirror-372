# Copyright 2023-2025 Geoffrey R. Scheller
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Sentinels
=========

Sentinel classes implemented as singletons, ``H`` is bounded by Hashable.

+--------------+-------------------+-------------------------------------------------+
| Module       | Sentinel          | Represents                                      |
+==============+===================+=================================================+
| ``novalue``  | ``NoValue()``     | actually missing value, not potentially missing |
+--------------+-------------------+-------------------------------------------------+
| ``flavored`` | ``Sentinel[H]()`` | distinct sentinels indexed by hashable values   |
+--------------+-------------------+-------------------------------------------------+

"""

__author__ = 'Geoffrey R. Scheller'
__copyright__ = 'Copyright (c) 2023-2025 Geoffrey R. Scheller'
__license__ = 'Apache License 2.0'
