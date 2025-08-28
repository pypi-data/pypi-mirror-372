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

"""Singleton class representing a missing value.

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

====

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

====

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

====

Of course, we can also compare directly by identity.

.. code:: python

    if x is NoValue():
        print('nobody home')
        ...

.. warning::

    Threadsafe only if instantiated before going multi-threaded.

.. warning::

    Non-standard (unpythonic?) ``==`` and ``!=`` comparison operators.

"""

from typing import ClassVar

__all__ = ['NoValue']


class NoValue:
    __slots__ = ()

    _instance: 'ClassVar[NoValue | None]' = None

    def __new__(cls) -> 'NoValue':
        """
        :returns: The ``NoValue`` singleton instance.
        """
        if cls._instance is None:
            cls._instance = super(NoValue, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        return

    def __repr__(self) -> str:
        return 'NoValue()'

    def __eq__(self, other: object) -> bool:
        return False

    def __ne__(self, other: object) -> bool:
        return False
