from .address import Address

from typing import Dict


Environment = Dict[str, Address]


def empty_env() -> Environment:
    return dict()


def extend_env(env: Environment, name: str, addr: Address) -> Environment:
    new_env = env.copy()
    new_env[name] = addr
    return new_env
