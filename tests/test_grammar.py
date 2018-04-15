from viper.lexer import lex_line
from viper.parser import GRAMMAR
from viper.parser.ast.nodes import *

import viper.lexer as vl

import pytest


@pytest.mark.parametrize('line,ast', [
    ('foo',
     Name(vl.Name('foo'))),
    ('42',
     Number(vl.Number('42'))),
    ('...',
     Ellipsis()),
    ('()',
     ParenExpr(None)),
    ('(foo)',
     ParenExpr(OpExprList([OpExpr([], Expr(Name(vl.Name('foo')), []), [], [])]))),
])
def test_atom(line: str, ast: AST):
    lexemes = lex_line(line)
    assert ast == GRAMMAR.parse_rule('atom', lexemes)


@pytest.mark.parametrize('line,ast', [
    ('foo',
     Expr(Name(vl.Name('foo')), [])),
    ('foo.bar',
     Expr(Name(vl.Name('foo')), [Field(vl.Name('bar'))])),
    ('foo.bar.baz',
     Expr(Name(vl.Name('foo')), [Field(vl.Name('bar')), Field(vl.Name('baz'))])),
    ('foo.bar(baz)',
     Expr(Name(vl.Name('foo')), [Field(vl.Name('bar')), Call([Expr(Name(vl.Name('baz')), [])])])),
    ('foo.bar(baz, qux)',
     Expr(Name(vl.Name('foo')), [
         Field(vl.Name('bar')),
         Call([Expr(Name(vl.Name('baz')), []), Expr(Name(vl.Name('qux')), [])])
     ])),
    ('foo.bar(baz, qux.quum())',
     Expr(Name(vl.Name('foo')), [
         Field(vl.Name('bar')),
         Call([
             Expr(Name(vl.Name('baz')), []),
             Expr(Name(vl.Name('qux')), [Field(vl.Name('quum')), Call(None)])
         ])
     ])),
    ('2.foo',
     Expr(Number(vl.Number('2')), [Field(vl.Name('foo'))])),
])
def test_expr(line: str, ast: AST):
    lexemes = lex_line(line)
    assert ast == GRAMMAR.parse_rule('expr', lexemes)


@pytest.mark.parametrize('line,ast', [
    ('foo bar: Baz',
     Parameter(vl.Name('foo'), vl.Name('bar'), vl.Class('Baz'))),
    ('bar: Baz',
     Parameter(None, vl.Name('bar'), vl.Class('Baz'))),
])
def test_parameter(line: str, ast: AST):
    lexemes = lex_line(line)
    assert ast == GRAMMAR.parse_rule('parameter', lexemes)


@pytest.mark.parametrize('line,ast', [
    ('def foo() -> Bar: pass',
     FuncDef(vl.Name('foo'), None, vl.Class('Bar'), SimpleSuite(SimpleStmt(PassStmt())))),
    ('def foo(bar: Baz) -> Qux: pass',
     FuncDef(vl.Name('foo'),
             [
                 Parameter(None, vl.Name('bar'), vl.Class('Baz'))
             ],
             vl.Class('Qux'),
             SimpleSuite(SimpleStmt(PassStmt())))),
    ('def foo(a b: C, d: E, f g: H) -> I: pass',
     FuncDef(vl.Name('foo'),
             [
                 Parameter(vl.Name('a'), vl.Name('b'), vl.Class('C')),
                 Parameter(None, vl.Name('d'), vl.Class('E')),
                 Parameter(vl.Name('f'), vl.Name('g'), vl.Class('H'))
             ],
             vl.Class('I'),
             SimpleSuite(SimpleStmt(PassStmt())))),
])
def test_func_def(line: str, ast: AST):
    lexemes = lex_line(line)
    lexemes.append(vl.NEWLINE)
    assert ast == GRAMMAR.parse_rule('func_def', lexemes)
