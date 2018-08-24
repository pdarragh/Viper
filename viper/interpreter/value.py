from .environment import Environment

from viper.parser.ast.nodes import Expr


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
    def __init__(self, name: str, expr: Expr, env: Environment):
        self.name = name
        self.expr = expr
        self.env = env

    def __repr__(self) -> str:
        return f"CloVal({self.name}, {self.expr}, {self.env})"


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
