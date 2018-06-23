from .environment import Environment

from viper.parser.ast.nodes import Expr


class Value:
    pass


class TupleVal(Value):
    def __init__(self, *vals: Value):
        self.vals = list(vals)


class PathVal(Value):
    def __init__(self, root: str, *parts: str):
        self.root = root
        self.parts = list(parts)


class NameVal(Value):
    def __init__(self, name: str):
        self.name = name


class NamelessVal(Value):
    pass


class ClassVal(Value):
    def __init__(self, name: str):
        self.name = name


class NumVal(Value):
    def __init__(self, val: str):
        self.val = val


class CloVal(Value):
    def __init__(self, name: str, expr: Expr, env: Environment):
        self.name = name
        self.expr = expr
        self.env = env


class BoolVal(Value):
    pass


class TrueVal(BoolVal):
    pass


class FalseVal(BoolVal):
    pass


class UnitVal(Value):
    pass


class BottomVal(Value):
    pass


class EllipsisVal(Value):
    pass
