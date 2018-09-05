from ..value import ForeignCloVal


def plus(a: int, b: int) -> int:
    return a + b


def minus(a: int, b: int) -> int:
    return a - b


def times(a: int, b: int) -> int:
    return a * b


def divide(a: int, b: int) -> float:
    return a / b


def equals(a: int, b: int) -> bool:
    return a == b


env = {
    '+': ForeignCloVal(plus, {}),
    '-': ForeignCloVal(minus, {}),
    '*': ForeignCloVal(times, {}),
    '/': ForeignCloVal(divide, {}),
    '==': ForeignCloVal(equals, {}),
}