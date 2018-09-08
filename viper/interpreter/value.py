from .access import *
from .environment import Address, Environment

from viper.lexer import Class
from viper.parser.ast.nodes import AST, Parameter, FuncDef

from inspect import signature
from typing import Callable, Dict, List, NamedTuple


class StaticField(NamedTuple):
    addr: Address
    access: Access


class StaticMethod(NamedTuple):
    addr: Address
    access: Access


class InstanceField(NamedTuple):
    name: str
    access: Access


class InstanceMethod(NamedTuple):
    func: FuncDef
    access: Access


class Value:
    pass


class TupleVal(Value):
    def __init__(self, *vals: Value):
        self.vals = list(vals)

    def __repr__(self) -> str:
        return f"TupleVal({', '.join(map(str, self.vals))})"

    def __str__(self) -> str:
        return '(' + ', '.join(map(str, self.vals)) + ')'


class IntVal(Value):
    def __init__(self, val: str):
        self.val = val

    def __repr__(self) -> str:
        return f"IntVal({self.val})"

    def __str__(self) -> str:
        return str(self.val)


class FloatVal(Value):
    def __init__(self, val: str):
        self.val = val

    def __repr__(self) -> str:
        return f"FloatVal({self.val})"

    def __str__(self) -> str:
        return str(self.val)


class CloVal(Value):
    def __init__(self, params: List[Parameter], code: AST, env: Environment):
        self.params = params
        self.code = code
        self.env = env

    def __repr__(self) -> str:
        return f"CloVal(({', '.join(map(lambda p: str(p.internal), self.params))}), {self.env})"

    def __str__(self) -> str:
        return 'λ(' + ', '.join(map(lambda p: str(p.internal), self.params)) + ')'


class ForeignCloVal(Value):
    def __init__(self, func: Callable, env: Environment):
        self.params: List[str] = list(signature(func).parameters)
        self.func = func
        self.env = env

    def __repr__(self) -> str:
        return f"ForeignCloVal(({', '.join(self.params)}), {self.env})"

    def __str__(self) -> str:
        return 'pyλ(' + ', '.join(self.params) + ')'


class ClassDeclVal(Value):
    def __init__(self, parents: List[Class],
                 static_fields: Dict[str, StaticField], static_methods: Dict[str, StaticMethod],
                 instance_fields: List[InstanceField], instance_methods: List[InstanceMethod],
                 env: Environment):
        self.parents = list(map(lambda c: c.text, parents))
        self.static_fields = static_fields
        self.static_methods = static_methods
        self.instance_fields = instance_fields
        self.instance_methods = instance_methods
        self.env = env


class BoolVal(Value):
    def __repr__(self) -> str:
        return "BoolVal"


class TrueVal(BoolVal):
    def __repr__(self) -> str:
        return "TrueVal"

    def __str__(self) -> str:
        return 'true'


class FalseVal(BoolVal):
    def __repr__(self) -> str:
        return "FalseVal"

    def __str__(self) -> str:
        return 'false'


class UnitVal(Value):
    def __repr__(self) -> str:
        return "UnitVal"

    def __str__(self) -> str:
        return '()'


class BottomVal(Value):
    def __repr__(self) -> str:
        return "BottomVal"


class EllipsisVal(Value):
    def __repr__(self) -> str:
        return "EllipsisVal"

    def __str__(self) -> str:
        return '...'


def val_to_python(val: Value):
    if isinstance(val, IntVal):
        return int(val.val)
    elif isinstance(val, FloatVal):
        return float(val.val)
    elif isinstance(val, TrueVal):
        return True
    elif isinstance(val, FalseVal):
        return False
    else:
        raise RuntimeError(f"Cannot convert Value to native Python value: {val}")  # TODO: Use custom error.


def python_to_val(py) -> Value:
    if isinstance(py, bool):
        if py:
            return TrueVal()
        else:
            return FalseVal()
    elif isinstance(py, int):
        return IntVal(str(py))
    elif isinstance(py, float):
        return FloatVal(str(py))
    else:
        raise RuntimeError(f"Cannot convert native Python value to Value: {py}")  # TODO: Use custom error.
