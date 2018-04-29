# This module was automatically generated.


import viper.lexer as vl
from .ast import AST
from typing import List, Optional


class SingleInput(AST):
    pass


class FileLines(AST):
    pass


class Suite(AST):
    pass


class Stmt(AST):
    pass


class ExprStmt(AST):
    pass


class Atom(AST):
    pass


class Trailer(AST):
    pass


class Parameter(AST):
    def __init__(self, external: Optional[vl.Name], internal: vl.Name, param_type: vl.Class):
        self.external = external
        self.internal = internal
        self.param_type = param_type


class FileInput(AST):
    def __init__(self, lines: List[FileLines]):
        self.lines = lines


class SimpleStmt(Stmt):
    def __init__(self, expr_stmt: ExprStmt):
        self.expr_stmt = expr_stmt


class CompoundStmt(Stmt):
    pass


class Value(AST):
    def __init__(self, atom: Atom, trailers: List[Trailer]):
        self.atom = atom
        self.trailers = trailers


class SingleNewline(SingleInput):
    pass


class FileNewline(FileLines):
    pass


class FileStmt(FileLines):
    def __init__(self, stmt: Stmt):
        self.stmt = stmt


class ComplexSuite(Suite):
    def __init__(self, stmts: List[Stmt]):
        self.stmts = stmts


class PassStmt(ExprStmt):
    pass


class Name(Atom):
    def __init__(self, name: vl.Name):
        self.name = name


class Number(Atom):
    def __init__(self, num: vl.Number):
        self.num = num


class Ellipsis(Atom):
    pass


class Field(Trailer):
    def __init__(self, field: vl.Name):
        self.field = field


class SubOpExpr(AST):
    def __init__(self, op: vl.Operator, expr: Value):
        self.op = op
        self.expr = expr


class FuncDef(CompoundStmt):
    def __init__(self, name: vl.Name, params: List[Parameter], func_type: vl.Class, body: Suite):
        self.name = name
        self.params = params
        self.func_type = func_type
        self.body = body


class Arguments(AST):
    def __init__(self, args: List[Value]):
        self.args = args


class SimpleLine(SingleInput):
    def __init__(self, line: SimpleStmt):
        self.line = line


class ComplexLine(SingleInput):
    def __init__(self, line: CompoundStmt):
        self.line = line


class SimpleSuite(Suite):
    def __init__(self, stmt: SimpleStmt):
        self.stmt = stmt


class Call(Trailer):
    def __init__(self, args: List[Value]):
        self.args = args


class OpExpr(AST):
    def __init__(self, left_op: Optional[vl.Operator], expr: Value, sub_op_exprs: List[SubOpExpr], right_op: Optional[vl.Operator]):
        self.left_op = left_op
        self.expr = expr
        self.sub_op_exprs = sub_op_exprs
        self.right_op = right_op


class ClassDef(CompoundStmt):
    def __init__(self, name: vl.Class, args: Optional[Arguments], body: Suite):
        self.name = name
        self.args = args
        self.body = body


class InterfaceDef(CompoundStmt):
    def __init__(self, name: vl.Class, args: Optional[Arguments], body: Suite):
        self.name = name
        self.args = args
        self.body = body


class DataDef(CompoundStmt):
    def __init__(self, name: vl.Class, args: Optional[Arguments], body: Suite):
        self.name = name
        self.args = args
        self.body = body


class NotTest(AST):
    def __init__(self, tests: List[OpExpr]):
        self.tests = tests


class OpExprList(AST):
    def __init__(self, op_exprs: List[OpExpr]):
        self.op_exprs = op_exprs


class PlainExpr(ExprStmt):
    def __init__(self, expr: OpExpr):
        self.expr = expr


class AndTest(AST):
    def __init__(self, tests: List[NotTest]):
        self.tests = tests


class ReturnStmt(ExprStmt):
    def __init__(self, exprs: OpExprList):
        self.exprs = exprs


class ParenExpr(Atom):
    def __init__(self, expr_list: OpExprList):
        self.expr_list = expr_list


class OrTest(AST):
    def __init__(self, tests: List[AndTest]):
        self.tests = tests


class Test(AST):
    def __init__(self, test: OrTest):
        self.test = test


class IfExpr(CompoundStmt):
    def __init__(self, cond: Test, true_body: Suite, false_body: Suite):
        self.cond = cond
        self.true_body = true_body
        self.false_body = false_body
