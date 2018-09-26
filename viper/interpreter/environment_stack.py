from .environment import *

from copy import deepcopy
from itertools import chain
from typing import List, Mapping, Optional


"""
components:
    - stack of environments
    
operations:
    - push a new environment
    - pop last environment
    - search environments
    - bind name in environment

"""


class EnvironmentStack(Mapping[str, Address]):
    def __init__(self):
        self._envs: List[Environment] = [empty_env()]

    def _lookup_env_for_name(self, name: str) -> Optional[Environment]:
        for env in reversed(self._envs):
            if name in env:
                return env
        return None

    @property
    def top(self) -> Environment:
        return self._envs[-1]

    def __getitem__(self, name: str) -> Address:
        addr = self.get(name)
        if addr is None:
            raise KeyError(f"No such name in environment: {name}")
        return addr

    def __iter__(self):
        for env in reversed(self._envs):
            for name in reversed(env):
                yield name

    def __len__(self) -> int:
        return sum(map(len, self._envs))

    def __repr__(self) -> str:
        return repr(self._envs)

    def get(self, name: str) -> Optional[Address]:
        env = self._lookup_env_for_name(name)
        if env is None:
            return None
        return env[name]

    def push(self):
        self._envs.append(empty_env())

    def pop(self) -> Environment:
        if len(self._envs) > 1:
            return self._envs.pop()
        else:
            raise IndexError(f"Cannot pop global environment")

    def bind(self, name: str, addr: Address):
        self.top[name] = addr

    def __copy__(self):
        cls = self.__class__
        new_stack = cls.__new__(cls)
        new_stack._envs = self._envs.copy()

    def __deepcopy__(self, memo):
        cls = self.__class__
        new_stack = cls.__new__(cls)
        new_stack._envs = deepcopy(self._envs)
        return new_stack

    def clone(self) -> 'EnvironmentStack':
        return self.__deepcopy__({})
