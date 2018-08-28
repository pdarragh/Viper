from .environment import Environment

from viper.parser.ast.nodes import AST, Parameter

from inspect import signature
from typing import Callable, List


class Value:
    pass


class TupleVal(Value):
    def __init__(self, *vals: Value):
        self.vals = list(vals)

    def __repr__(self) -> str:
        return f"TupleVal({', '.join(map(str, self.vals))})"


class NumVal(Value):
    def __init__(self, val: str):
        self.val = val

    def __repr__(self) -> str:
        return f"NumVal({self.val})"


class CloVal(Value):
    def __init__(self, params: List[Parameter], code: AST, env: Environment):
        self.params = params
        self.code = code
        self.env = env

    def __repr__(self) -> str:
        return f"CloVal(({', '.join(map(lambda p: p.internal, self.params))}), {self.env})"


class ForeignCloVal(Value):
    def __init__(self, func: Callable, env: Environment):
        self.params: List[str] = list(signature(func).parameters)
        self.func = func
        self.env = env

    def __repr__(self) -> str:
        return f"ForeignCloVal(({', '.join(self.params)}), {self.env})"


class BoolVal(Value):
    def __repr__(self) -> str:
        return "BoolVal"


class TrueVal(BoolVal):
    def __repr__(self) -> str:
        return "TrueVal"


class FalseVal(BoolVal):
    def __repr__(self) -> str:
        return "FalseVal"


class UnitVal(Value):
    def __repr__(self) -> str:
        return "UnitVal"


class BottomVal(Value):
    def __repr__(self) -> str:
        return "BottomVal"


class EllipsisVal(Value):
    def __repr__(self) -> str:
        return "EllipsisVal"


def val_to_python(val: Value):
    if isinstance(val, NumVal):
        num_val = float(val.val)
        if num_val.is_integer():
            num_val = int(num_val)
        return num_val
    elif isinstance(val, TrueVal):
        return True
    elif isinstance(val, FalseVal):
        return False
    else:
        raise RuntimeError(f"Cannot convert Value to native Python value: {val}")  # TODO: Use custom error.


def python_to_val(py) -> Value:
    if isinstance(py, int) or isinstance(py, float):
        return NumVal(str(py))
    elif isinstance(py, bool):
        if py:
            return TrueVal()
        else:
            return FalseVal()
    else:
        raise RuntimeError(f"Cannot convert native Python value to Value: {py}")  # TODO: Use custom error.
