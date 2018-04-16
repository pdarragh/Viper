from viper.lexer import lex_line
from viper.parser import GRAMMAR
from viper.parser.ast.nodes import *

import viper.lexer as vl

import pytest


def run_test(rule: str, ast: AST, lexemes: List[vl.Lexeme], prepend: List[vl.Lexeme], append: List[vl.Lexeme]):
    assert ast == GRAMMAR.parse_rule(rule, prepend + lexemes + append)


@pytest.mark.parametrize('line,ast', [
    ('foo',
     Name(vl.Name('foo'))),
    ('42',
     Number(vl.Number('42'))),
    ('...',
     Ellipsis()),
    ('()',
     ParenExpr(OpExprList([]))),
    ('(foo)',
     ParenExpr(OpExprList([OpExpr(None, Expr(Name(vl.Name('foo')), []), [], None)]))),
])
def test_atom(line: str, ast: AST):
    lexemes = lex_line(line)
    run_test('atom', ast, lexemes, [], [])


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
             Expr(Name(vl.Name('qux')), [Field(vl.Name('quum')), Call([])])
         ])
     ])),
    ('2.foo',
     Expr(Number(vl.Number('2')), [Field(vl.Name('foo'))])),
])
def test_expr(line: str, ast: AST):
    lexemes = lex_line(line)
    run_test('expr', ast, lexemes, [], [])


@pytest.mark.parametrize('line,ast', [
    ('foo',
     OpExpr(None, Expr(Name(vl.Name('foo')), []), [], None)),
    ('++ foo',
     OpExpr(vl.Operator('++'), Expr(Name(vl.Name('foo')), []), [], None)),
    ('++ foo --',
     OpExpr(vl.Operator('++'), Expr(Name(vl.Name('foo')), []), [], vl.Operator('--'))),
    ('++ foo || bar --',
     OpExpr(
         vl.Operator('++'),
         Expr(Name(vl.Name('foo')), []),
         [SubOpExpr(
             vl.Operator('||'),
             Expr(Name(vl.Name('bar')), [])
         )],
         vl.Operator('--')
     )),
    ('++ foo ** bar || baz // qux',
     OpExpr(
         vl.Operator('++'),
         Expr(Name(vl.Name('foo')), []),
         [
             SubOpExpr(vl.Operator('**'), Expr(Name(vl.Name('bar')), [])),
             SubOpExpr(vl.Operator('||'), Expr(Name(vl.Name('baz')), [])),
             SubOpExpr(vl.Operator('//'), Expr(Name(vl.Name('qux')), []))
         ],
         None
     )),
])
def test_op_expr(line: str, ast: AST):
    lexemes = lex_line(line)
    run_test('op_expr', ast, lexemes, [], [])


@pytest.mark.parametrize('line,ast', [
    ('pass',
     SimpleSuite(SimpleStmt(PassStmt()))),
    ('return',
     SimpleSuite(SimpleStmt(ReturnStmt(OpExprList([]))))),
    ('return foo',
     SimpleSuite(SimpleStmt(ReturnStmt(OpExprList([OpExpr(None, Expr(Name(vl.Name('foo')), []), [], None)]))))),
    ('foo, ~bar, baz !',
     SimpleSuite(SimpleStmt(OpExprList([
         OpExpr(None, Expr(Name(vl.Name('foo')), []), [], None),
         OpExpr(vl.Operator('~'), Expr(Name(vl.Name('bar')), []), [], None),
         OpExpr(None, Expr(Name(vl.Name('baz')), []), [], vl.Operator('!'))
     ])))),
])
def test_simple_suite(line: str, ast: AST):
    lexemes = lex_line(line)
    run_test('suite', ast, lexemes, [], [vl.NEWLINE])


@pytest.mark.parametrize('line,ast', [
    ('foo bar: Baz',
     Parameter(vl.Name('foo'), vl.Name('bar'), vl.Class('Baz'))),
    ('bar: Baz',
     Parameter(None, vl.Name('bar'), vl.Class('Baz'))),
])
def test_parameter(line: str, ast: AST):
    lexemes = lex_line(line)
    run_test('parameter', ast, lexemes, [], [])


@pytest.mark.parametrize('line,ast', [
    ('def foo() -> Bar: pass',
     FuncDef(vl.Name('foo'), [], vl.Class('Bar'), SimpleSuite(SimpleStmt(PassStmt())))),
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
    run_test('func_def', ast, lexemes, [], [vl.NEWLINE])
