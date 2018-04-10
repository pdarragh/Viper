# This module was automatically generated.

from typing import List, Optional


class AST:
    pass


class Stmt(AST):
    pass


class Atom(AST):
    pass


class SingleInput(AST):
    pass


class Trailer(AST):
    pass


class Suite(AST):
    pass


class FileLines(AST):
    pass


class ExprStmt(AST):
    pass


class Parameter(AST):
    def __init__(self, external: str, internal: str, param_type: str):
        self.external = external
        self.internal = internal
        self.param_type = param_type


class SimpleStmt(Stmt):
    def __init__(self, expr_stmt: ExprStmt):
        self.expr_stmt = expr_stmt


class CompoundStmt(Stmt):
    pass


class FileInput(AST):
    def __init__(self, lines: List[FileLines]):
        self.lines = lines


class Field(Trailer):
    def __init__(self, field: str):
        self.field = field


class Ellipsis(Atom):
    pass


class FileStmt(FileLines):
    def __init__(self, stmt: Stmt):
        self.stmt = stmt


class ComplexSuite(Suite):
    def __init__(self, stmt: Stmt, stmts: List[Stmt]):
        self.stmt = stmt
        self.stmts = stmts


class PassStmt(ExprStmt):
    pass


class SingleNewline(SingleInput):
    pass


class Expr(AST):
    def __init__(self, atom: Atom, trailers: List[Trailer]):
        self.atom = atom
        self.trailers = trailers


class Name(Atom):
    def __init__(self, name: str):
        self.name = name


class FileNewline(FileLines):
    pass


class Number(Atom):
    def __init__(self, num: str):
        self.num = num


class ComplexLine(SingleInput):
    def __init__(self, line: CompoundStmt):
        self.line = line


class SimpleLine(SingleInput):
    def __init__(self, line: SimpleStmt):
        self.line = line


class SubOpExpr(AST):
    def __init__(self, first_op: str, ops: str, expr: Expr):
        self.first_op = first_op
        self.ops = ops
        self.expr = expr


class FuncDef(CompoundStmt):
    def __init__(self, name: str, params: List[Parameter], func_type: str, body: Suite):
        self.name = name
        self.params = params
        self.func_type = func_type
        self.body = body


class SimpleSuite(Suite):
    def __init__(self, stmt: SimpleStmt):
        self.stmt = stmt


class ExprList(AST):
    def __init__(self, exprs: List[Expr]):
        self.exprs = exprs


class Arguments(AST):
    def __init__(self, args: List[Expr]):
        self.args = args


class ClassDef(CompoundStmt):
    def __init__(self, name: str, args: Optional[Arguments], body: Suite):
        self.name = name
        self.args = args
        self.body = body


class InterfaceDef(CompoundStmt):
    def __init__(self, name: str, args: Optional[Arguments], body: Suite):
        self.name = name
        self.args = args
        self.body = body


class Args(Trailer):
    def __init__(self, args: Arguments):
        self.args = args


class OpExpr(AST):
    def __init__(self, left_ops: str, expr: Expr, sub_op_exprs: List[SubOpExpr], right_ops: str):
        self.left_ops = left_ops
        self.expr = expr
        self.sub_op_exprs = sub_op_exprs
        self.right_ops = right_ops


class DataDef(CompoundStmt):
    def __init__(self, name: str, args: Optional[Arguments], body: Suite):
        self.name = name
        self.args = args
        self.body = body


class OpExprList(ExprStmt):
    def __init__(self, op_exprs: List[OpExpr]):
        self.op_exprs = op_exprs


class ParenExpr(Atom):
    def __init__(self, expr_list: Optional[OpExprList]):
        self.expr_list = expr_list


class ReturnStmt(ExprStmt):
    def __init__(self, exprs: Optional[OpExprList]):
        self.exprs = exprs
