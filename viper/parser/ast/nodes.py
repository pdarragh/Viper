# This module was automatically generated.


import viper.lexer as vl
from .ast import AST
from typing import List, Optional


class SingleInput(AST):
    pass


class Term(AST):
    pass


class FileLine(AST):
    pass


class PlainStmt(AST):
    pass


class Parameter(AST):
    def __init__(self, external: Optional[vl.Name], internal: vl.Name, param_type: vl.Class):
        self.external = external
        self.internal = internal
        self.param_type = param_type


class StmtBlock(AST):
    pass


class Atom(AST):
    pass


class Trailer(AST):
    pass


class ExprBlock(AST):
    pass


class Pattern(AST):
    pass


class FileInput(AST):
    def __init__(self, lines: List[FileLine]):
        self.lines = lines


class Stmt(Term):
    pass


class EmptyStmt(PlainStmt):
    pass


class ElseStmt(AST):
    def __init__(self, else_body: StmtBlock):
        self.else_body = else_body


class Expr(Term):
    pass


class ElseExpr(AST):
    def __init__(self, else_body: ExprBlock):
        self.else_body = else_body


class AtomExpr(AST):
    def __init__(self, atom: Atom, trailers: List[Trailer]):
        self.atom = atom
        self.trailers = trailers


class SimplePattern(Pattern):
    pass


class PatternList(AST):
    def __init__(self, patterns: List[Pattern]):
        self.patterns = patterns


class SingleNewline(SingleInput):
    pass


class SingleLine(SingleInput):
    def __init__(self, line: Term):
        self.line = line


class FileNewline(FileLine):
    pass


class NameAtom(Atom):
    def __init__(self, name: vl.Name):
        self.name = name


class NumberAtom(Atom):
    def __init__(self, num: vl.Number):
        self.num = num


class EllipsisAtom(Atom):
    pass


class Field(Trailer):
    def __init__(self, field: vl.Name):
        self.field = field


class NamedPattern(Pattern):
    def __init__(self, name: vl.Name, pat_type: vl.Class):
        self.name = name
        self.pat_type = pat_type


class NamelessPattern(Pattern):
    def __init__(self, pat_type: vl.Class):
        self.pat_type = pat_type


class AssignStmt(PlainStmt):
    def __init__(self, name: vl.Name, expr: Expr):
        self.name = name
        self.expr = expr


class Definition(Stmt):
    pass


class Arguments(AST):
    def __init__(self, args: List[AtomExpr]):
        self.args = args


class SubOpExpr(AST):
    def __init__(self, op: vl.Operator, atom: AtomExpr):
        self.op = op
        self.atom = atom


class FileStmt(FileLine):
    def __init__(self, stmt: Stmt):
        self.stmt = stmt


class SimpleStmt(Stmt):
    def __init__(self, stmt: PlainStmt):
        self.stmt = stmt


class SimpleStmtBlock(StmtBlock):
    def __init__(self, stmt: Stmt):
        self.stmt = stmt


class CompoundStmtBlock(StmtBlock):
    def __init__(self, stmts: List[Stmt]):
        self.stmts = stmts


class Call(Trailer):
    def __init__(self, args: List[AtomExpr]):
        self.args = args


class SimpleExprBlock(ExprBlock):
    def __init__(self, expr: Expr):
        self.expr = expr


class IndentedExprBlock(ExprBlock):
    def __init__(self, expr: Expr):
        self.expr = expr


class SimpleNamedPattern(SimplePattern):
    def __init__(self, name: vl.Name):
        self.name = name


class SimpleNamelessPattern(SimplePattern):
    pass


class SimpleParenPattern(SimplePattern):
    def __init__(self, pattern_list: Optional[PatternList]):
        self.pattern_list = pattern_list


class FuncDef(Definition):
    def __init__(self, name: vl.Name, params: List[Parameter], func_type: vl.Class, body: StmtBlock):
        self.name = name
        self.params = params
        self.func_type = func_type
        self.body = body


class ClassDef(Definition):
    def __init__(self, name: vl.Class, args: Optional[Arguments], body: StmtBlock):
        self.name = name
        self.args = args
        self.body = body


class InterfaceDef(Definition):
    def __init__(self, name: vl.Class, args: Optional[Arguments], body: StmtBlock):
        self.name = name
        self.args = args
        self.body = body


class DataDef(Definition):
    def __init__(self, name: vl.Class, args: Optional[Arguments], body: StmtBlock):
        self.name = name
        self.args = args
        self.body = body


class OpExpr(AST):
    def __init__(self, left_op: Optional[vl.Operator], atom: AtomExpr, sub_op_exprs: List[SubOpExpr], right_op: Optional[vl.Operator]):
        self.left_op = left_op
        self.atom = atom
        self.sub_op_exprs = sub_op_exprs
        self.right_op = right_op


class NotTestExpr(AST):
    def __init__(self, tests: List[OpExpr]):
        self.tests = tests


class AndTestExpr(AST):
    def __init__(self, tests: List[NotTestExpr]):
        self.tests = tests


class OrTestExpr(AST):
    def __init__(self, tests: List[AndTestExpr]):
        self.tests = tests


class TestExpr(AST):
    def __init__(self, test: OrTestExpr):
        self.test = test


class ElifStmt(AST):
    def __init__(self, cond: TestExpr, elif_body: StmtBlock):
        self.cond = cond
        self.elif_body = elif_body


class ElifExpr(AST):
    def __init__(self, cond: TestExpr, elif_body: ExprBlock):
        self.cond = cond
        self.elif_body = elif_body


class TestExprList(Expr):
    def __init__(self, tests: List[TestExpr]):
        self.tests = tests


class ReturnStmt(PlainStmt):
    def __init__(self, tests: Optional[TestExprList]):
        self.tests = tests


class IfStmt(Stmt):
    def __init__(self, cond: TestExpr, then_body: StmtBlock, elif_stmts: List[ElifStmt], else_stmt: Optional[ElseStmt]):
        self.cond = cond
        self.then_body = then_body
        self.elif_stmts = elif_stmts
        self.else_stmt = else_stmt


class IfExpr(Expr):
    def __init__(self, cond: TestExpr, then_body: ExprBlock, elif_exprs: List[ElifExpr], else_expr: Optional[ElseExpr]):
        self.cond = cond
        self.then_body = then_body
        self.elif_exprs = elif_exprs
        self.else_expr = else_expr


class ParenAtom(Atom):
    def __init__(self, tests: Optional[TestExprList]):
        self.tests = tests
