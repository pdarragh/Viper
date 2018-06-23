from .address import Address

from typing import Dict


Environment = Dict[str, Address]


def empty_env() -> Environment:
    return Environment()


def extend_env(env: Environment, name: str, value: Address) -> Environment:
    new_env = env.copy()
    new_env[name] = value
    return new_env
