# This module was automatically generated.

import viper.lexer as vl

from typing import List, Optional


class AST:
    def __eq__(self, other):
        if not type(other) == type(self):
            return False
        my_vars = vars(self)
        other_vars = vars(other)
        for var, val in my_vars.items():
            if not var in other_vars:
                return False
            if val != other_vars[var]:
                return False
        return True

    def __repr__(self):
        my_vars = vars(self)
        return self.__class__.__name__ + '(' + ', '.join(k + '=' + repr(v) for k, v in my_vars.items()) + ')'

    def __str__(self):
        return repr(self)


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


class Expr(AST):
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
    def __init__(self, op: vl.Operator, expr: Expr):
        self.op = op
        self.expr = expr


class ExprList(AST):
    def __init__(self, exprs: List[Expr]):
        self.exprs = exprs


class FuncDef(CompoundStmt):
    def __init__(self, name: vl.Name, params: List[Parameter], func_type: vl.Class, body: Suite):
        self.name = name
        self.params = params
        self.func_type = func_type
        self.body = body


class Arguments(AST):
    def __init__(self, args: List[Expr]):
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
    def __init__(self, args: List[Expr]):
        self.args = args


class OpExpr(AST):
    def __init__(self, left_op: Optional[vl.Operator], expr: Expr, sub_op_exprs: List[SubOpExpr], right_op: Optional[vl.Operator]):
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


class OpExprList(ExprStmt):
    def __init__(self, op_exprs: List[OpExpr]):
        self.op_exprs = op_exprs


class ReturnStmt(ExprStmt):
    def __init__(self, exprs: OpExprList):
        self.exprs = exprs


class ParenExpr(Atom):
    def __init__(self, expr_list: OpExprList):
        self.expr_list = expr_list
