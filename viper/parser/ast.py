from viper.lexer.lexemes import *


class AST:
    pass


class BinOp(AST):
    def __init__(self, op: Operator, left: Lexeme, right: Lexeme):
        self.op = op
        self.left = left
        self.right = right


class UnOpPre(AST):
    def __init__(self, op: Operator, arg: Lexeme):
        self.op = op
        self.arg = arg


class UnOpPost(AST):
    def __init__(self, arg: Lexeme, op: Operator):
        self.arg = arg
        self.op = op


class Num(AST):
    def __init__(self, token: Number):
        self.token = token
        self.value = float(token.text)
