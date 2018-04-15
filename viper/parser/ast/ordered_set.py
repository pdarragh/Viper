from collections import OrderedDict
from typing import Iterator, MutableSet, Set


class OrderedSet(MutableSet):
    def __init__(self):
        self._dict = OrderedDict()

    def add(self, x) -> None:
        self._dict[x] = None

    def discard(self, x) -> None:
        if x in self._dict:
            del(self._dict[x])

    def __contains__(self, x: object) -> bool:
        return x in self._dict

    def __len__(self) -> int:
        return len(self._dict)

    def __iter__(self) -> Iterator:
        return iter(self._dict)
