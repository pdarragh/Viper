from .environment_stack import Address, EnvironmentStack

from viper.lexer import Class
from viper.parser.ast.nodes import AST, Parameter, FuncDef

from inspect import signature
from typing import Any, Callable, Dict, List, NamedTuple


class InstantiatedField(NamedTuple):
    addr: Address


class InstantiatedMethod(NamedTuple):
    addr: Address


class UninstantiatedField(NamedTuple):
    name: str


class UninstantiatedMethod(NamedTuple):
    func: FuncDef


class Value:
    pass


class TupleVal(Value):
    def __init__(self, *vals: Value):
        self.vals = list(vals)

    def __repr__(self) -> str:
        return f"TupleVal({', '.join(map(str, self.vals))})"

    def __str__(self) -> str:
        return '(' + ', '.join(map(str, self.vals)) + ')'


class SimpleValue(Value):
    def __init__(self, val: str):
        self.val = val

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.val})"

    def __str__(self) -> str:
        return str(self.val)


class IntVal(SimpleValue):
    pass


class FloatVal(SimpleValue):
    pass


class StringVal(SimpleValue):
    def __str__(self) -> str:
        return '"' + super().__str__() + '"'


class CloVal(Value):
    def __init__(self, params: List[Parameter], code: AST, envs: EnvironmentStack):
        self.params = params
        self.code = code
        self.envs = envs

    def __repr__(self) -> str:
        return f"CloVal(({', '.join(map(lambda p: str(p.internal), self.params))}), {self.envs})"

    def __str__(self) -> str:
        return 'λ(' + ', '.join(map(lambda p: str(p.internal), self.params)) + ')'


class ForeignCloVal(Value):
    def __init__(self, func: Callable, env: Dict[str, Any]):
        self.params: List[str] = list(signature(func).parameters)
        self.func = func
        self.env = env

    def __repr__(self) -> str:
        return f"ForeignCloVal(({', '.join(self.params)}), {self.env})"

    def __str__(self) -> str:
        return 'pyλ(' + ', '.join(self.params) + ')'


class ClassDeclVal(Value):
    def __init__(self, name: str, parents: List[str],
                 static_fields: Dict[str, InstantiatedField], static_methods: Dict[str, InstantiatedMethod],
                 instance_fields: List[UninstantiatedField], instance_methods: List[UninstantiatedMethod],
                 envs: EnvironmentStack):
        self.name = name
        self.parents = parents
        self.static_fields = static_fields
        self.static_methods = static_methods
        self.instance_fields = instance_fields
        self.instance_methods = instance_methods
        self.envs = envs

    def __repr__(self) -> str:
        return f"ClassDeclVal"

    def __str__(self) -> str:
        return f"ClassDeclVal"


class ClassInstanceVal(Value):
    def __init__(self, cls: ClassDeclVal, instance_fields: Dict[str, InstantiatedField],
                 instance_methods: Dict[str, InstantiatedMethod]):
        self.cls = cls
        self.instance_fields = instance_fields
        self.instance_methods = instance_methods

    def __repr__(self) -> str:
        return f"ClassInstanceVal"

    def __str__(self) -> str:
        return f"ClassInstanceVal"


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
    elif isinstance(val, StringVal):
        return str(val.val)
    elif isinstance(val, TrueVal):
        return True
    elif isinstance(val, FalseVal):
        return False
    else:
        raise RuntimeError(f"Cannot convert Value to native Python value: {val}")  # TODO: Use custom error.


def python_to_val(py) -> Value:
    if py is None:
        return UnitVal()
    elif isinstance(py, bool):
        if py:
            return TrueVal()
        else:
            return FalseVal()
    elif isinstance(py, int):
        return IntVal(str(py))
    elif isinstance(py, float):
        return FloatVal(str(py))
    elif isinstance(py, str):
        return StringVal(str(py))
    else:
        raise RuntimeError(f"Cannot convert native Python value to Value: {py}")  # TODO: Use custom error.


def stringify_python_val(py) -> str:
    if isinstance(py, str):
        return repr(py)
    else:
        return str(py)
