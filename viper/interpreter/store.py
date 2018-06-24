from .address import Address
from .value import Value

from collections.abc import Mapping
from typing import Dict


class Store(Mapping):
    def __init__(self, next_address: Address, values: Dict[Address, Value]):
        self.dict: Dict[Address, Value] = values
        self.next_addr: Address = next_address

    def __getitem__(self, key: Address) -> Value:
        return self.dict[key]

    def __iter__(self):
        return iter(self.dict)

    def __len__(self) -> int:
        return len(self.dict)

    def __repr__(self) -> str:
        return f"Store({self.next_addr}, {self.dict})"


def empty_store() -> Store:
    return Store(0, {})


def extend_store(store: Store, value: Value, addr: Address = None) -> Store:
    new_values = store.dict.copy()
    if addr is None:
        new_values.update({store.next_addr: value})
        return Store(store.next_addr + 1, new_values)
    else:
        new_values.update({addr: value})
        return Store(store.next_addr, new_values)
