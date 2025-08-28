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

from typing import cast, ClassVar, Final, overload
from pythonic_fp.sentinels.flavored import Sentinel


class MyClass:
    _secret: Final[ClassVar[str]] = '_secret_str'
    _sentinel: Final[ClassVar[Sentinel[str]]] = Sentinel(_secret)

    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, value: float) -> None: ...
    @overload
    def __init__(self, value: None) -> None: ...
    @overload
    def __init__(self, value: float | None) -> None: ...

    def __init__(
        self, value: float | None | Sentinel[str] = Sentinel('_secret_str')
    ) -> None:
        if value is self._sentinel:
            self.value: float | None = 42.0
        else:
            self.value = cast(float | None, value)

    def get_value(self) -> float | None:
        return self.value


class TestHiddenImplementation:
    def test_hidden_inplemetation(self) -> None:
        my_0 = MyClass(0.0)
        my_1 = MyClass(1.0)
        my_42 = MyClass()
        my_none = MyClass(None)

        value: float | None

        if (value := my_0.get_value()) is None:
            assert False
        else:
            assert value == 0.0

        if (value := my_1.get_value()) is None:
            assert False
        else:
            assert value == 1.0

        if (value := my_42.get_value()) is None:
            assert False
        else:
            assert value == 42.0

        if (value := my_none.get_value()) is None:
            assert True
        else:
            assert value == 0.0
