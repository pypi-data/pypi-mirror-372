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

"""Sentinel values of different (hashable) flavors. Can be used
with functions or classes.

.. note::

   Threadsafe.

.. note::

   Can be compared using ``==`` and ``!=``. A flavored sentinel
   value always equals itself and never equals anything else,
   especially other flavored sentinel values.

   To ensure that reference equality is used put the known
   sentinel value first.

.. tip::

   - don't export when using as a hidden implementation detail.
   - does not clash with end user code

     - which may use either ``None`` or ``()`` as their "sentinel" values.


"""
import threading
from typing import ClassVar, final, Hashable, TypeVar

__all__ = ['Sentinel']

H = TypeVar("H", bound=Hashable)

@final
class Sentinel[H]:

    __slots__ = ('_flavor',)

    _flavors: 'dict[H, Sentinel[H]]' = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __new__(cls, flavor: H) -> 'Sentinel[H]':
        """
        :param flavor: Hashable value to determine the "flavor" of the ``Sentinel``.
        :returns: The ``Sentinel`` singleton instance with flavor ``flavor``.
        """
        if flavor not in cls._flavors:
            with cls._lock:
                if flavor not in cls._flavors:
                    cls._flavors[flavor] = super(Sentinel, cls).__new__(cls)
        return cls._flavors[flavor]

    def __init__(self, flavor: H) -> None:
        if not hasattr(self, '_flavor'):
            self._flavor = flavor

    def __repr__(self) -> str:
        return "Sentinel('" + repr(self._flavor) + "')"
