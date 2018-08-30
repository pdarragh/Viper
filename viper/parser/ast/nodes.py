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


class LhsExpr(AST):
    pass


class NotTestExpr(AST):
    pass


class Atom(AST):
    pass


class Trailer(AST):
    pass


class ExprBlock(AST):
    pass


class Id(AST):
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


class AndTestExpr(AST):
    def __init__(self, tests: List[NotTestExpr]):
        self.tests = tests


class AtomExpr(AST):
    def __init__(self, atom: Atom, trailers: List[Trailer]):
        self.atom = atom
        self.trailers = trailers


class Pattern(LhsExpr):
    pass


class VarId(Id):
    def __init__(self, id: vl.Name):
        self.id = id


class PathPart(AST):
    def __init__(self, part: Id):
        self.part = part


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


class TrueAtom(Atom):
    pass


class FalseAtom(Atom):
    pass


class Field(Trailer):
    def __init__(self, field: vl.Name):
        self.field = field


class ClassId(Id):
    def __init__(self, id: vl.Class):
        self.id = id


class AssignStmt(PlainStmt):
    def __init__(self, lhs: LhsExpr, expr: Expr):
        self.lhs = lhs
        self.expr = expr


class Definition(Stmt):
    pass


class Arguments(AST):
    def __init__(self, args: List[AtomExpr]):
        self.args = args


class OrTestExpr(AST):
    def __init__(self, tests: List[AndTestExpr]):
        self.tests = tests


class SubOpExpr(AST):
    def __init__(self, op: vl.Operator, atom: AtomExpr):
        self.op = op
        self.atom = atom


class TypedPattern(Pattern):
    pass


class PatternList(AST):
    def __init__(self, patterns: List[Pattern]):
        self.patterns = patterns


class Path(AST):
    def __init__(self, id: Id, parts: List[PathPart]):
        self.id = id
        self.parts = parts


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


class SimpleExprBlock(ExprBlock):
    def __init__(self, expr: Expr):
        self.expr = expr


class IndentedExprBlock(ExprBlock):
    def __init__(self, expr: Expr):
        self.expr = expr


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


class TestExpr(AST):
    def __init__(self, test: OrTestExpr):
        self.test = test


class OpExpr(AST):
    def __init__(self, left_op: Optional[vl.Operator], atom: AtomExpr, sub_op_exprs: List[SubOpExpr], right_op: Optional[vl.Operator]):
        self.left_op = left_op
        self.atom = atom
        self.sub_op_exprs = sub_op_exprs
        self.right_op = right_op


class SimplePattern(TypedPattern):
    pass


class TypedVariablePattern(TypedPattern):
    def __init__(self, id: VarId, pat_type: vl.Class):
        self.id = id
        self.pat_type = pat_type


class TypedAnonymousPattern(TypedPattern):
    def __init__(self, pat_type: vl.Class):
        self.pat_type = pat_type


class TypedFieldPattern(TypedPattern):
    def __init__(self, root: Expr, field: VarId, pat_type: vl.Class):
        self.root = root
        self.field = field
        self.pat_type = pat_type


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


class NegatedTestExpr(NotTestExpr):
    def __init__(self, op_expr: OpExpr):
        self.op_expr = op_expr


class NotNegatedTestExpr(NotTestExpr):
    def __init__(self, op_expr: OpExpr):
        self.op_expr = op_expr


class Call(Trailer):
    def __init__(self, args: List[TestExpr]):
        self.args = args


class SimpleVariablePattern(SimplePattern):
    def __init__(self, id: VarId):
        self.id = id


class SimpleAnonymousPattern(SimplePattern):
    pass


class SimpleFieldPattern(SimplePattern):
    def __init__(self, root: Expr, field: VarId):
        self.root = root
        self.field = field


class SimpleParenPattern(SimplePattern):
    def __init__(self, pattern_list: PatternList):
        self.pattern_list = pattern_list


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
