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
Missing Value Sentinel
======================

Singleton class representing a missing value.

In untyped Python, both ``None`` and ``()`` are often used by end users
and libraries as sentinel values. I prefer to think of them as

- ``None``: returned (or returns) no values
- ``()``: an empty, possibly typed, but still iterable collection

While ``NoValue()`` is a singleton object representing a missing value.

Given variables

.. code:: python

    x: int | NoValue
    y: int | NoValue

Equality between ``x`` and ``y`` means both values exist and compare as equal.
If one or both of theses values are missing, then what is there to compare?

.. table:: ``x == y``

   +-----------+-----------+--------+--------+
   |    x∖y    | NoValue() | 42     | 57     |
   +===========+===========+========+========+
   | NoValue() | false     | false  | false  |
   +-----------+-----------+--------+--------+
   | 42        | false     | true   | false  |
   +-----------+-----------+--------+--------+
   | 57        | false     | false  | true   |
   +-----------+-----------+--------+--------+

Similarly for not equals.

.. table:: ``x != y``

   +-----------+-----------+--------+--------+
   |    x∖y    | NoValue() | 42     | 57     |
   +===========+===========+========+========+
   | NoValue() | false     | false  | false  |
   +-----------+-----------+--------+--------+
   | 42        | false     | false  | true   |
   +-----------+-----------+--------+--------+
   | 57        | false     | true   | false  |
   +-----------+-----------+--------+--------+

.. note::

   Threadsafe.

.. warning::

   Do not use ``==`` or ``!=`` to identify ``NoValue()``,  compare
   directly by identity using ``is`` and ``is not``.

"""

import threading
from typing import ClassVar, final

__all__ = ['NoValue']


@final
class NoValue():
    __slots__ = ()

    _instance: 'ClassVar[NoValue | None]' = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __new__(cls) -> 'NoValue':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """
        :returns: The ``NoValue`` singleton instance.
        :rtype: ``NoValue``
        """
        return

    def __repr__(self) -> str:
        return 'NoValue()'

    def __eq__(self, other: object) -> bool:
        return False

    def __ne__(self, other: object) -> bool:
        return False
