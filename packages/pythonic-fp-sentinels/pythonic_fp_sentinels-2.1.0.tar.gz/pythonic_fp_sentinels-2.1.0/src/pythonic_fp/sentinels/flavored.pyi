from typing import Hashable, TypeVar

__all__ = ['Sentinel']

H = TypeVar('H', bound=Hashable)

class Sentinel[H]:
    def __new__(cls, flavor: H) -> Sentinel[H]: ...
    def __init__(self, flavor: H) -> None: ...
