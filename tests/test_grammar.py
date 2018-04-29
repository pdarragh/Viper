from viper.lexer import lex_line
from viper.parser import *

import viper.lexer as vl
import viper.parser.ast.nodes as ns

import pytest

from typing import List


def run_test(rule: str, ast: AST, lexemes: List[vl.Lexeme], prepend: List[vl.Lexeme], append: List[vl.Lexeme]):
    parse = GRAMMAR.parse_rule(rule, prepend + lexemes + append)
    assert isinstance(parse, SingleParse)
    assert ast == parse.ast


@pytest.mark.parametrize('line,ast', [
    ('foo',
     ns.Name(vl.Name('foo'))),
    ('42',
     ns.Number(vl.Number('42'))),
    ('...',
     ns.Ellipsis()),
    ('()',
     ns.ParenExpr(ns.OpExprList([]))),
    ('(foo)',
     ns.ParenExpr(ns.OpExprList([ns.OpExpr(None, ns.Value(ns.Name(vl.Name('foo')), []), [], None)]))),
])
def test_atom(line: str, ast: AST):
    lexemes = lex_line(line)
    run_test('atom', ast, lexemes, [], [])


@pytest.mark.parametrize('line,ast', [
    ('foo',
     ns.Value(ns.Name(vl.Name('foo')), [])),
    ('foo.bar',
     ns.Value(ns.Name(vl.Name('foo')), [ns.Field(vl.Name('bar'))])),
    ('foo.bar.baz',
     ns.Value(ns.Name(vl.Name('foo')), [ns.Field(vl.Name('bar')), ns.Field(vl.Name('baz'))])),
    ('foo.bar(baz)',
     ns.Value(ns.Name(vl.Name('foo')), [ns.Field(vl.Name('bar')), ns.Call([ns.Value(ns.Name(vl.Name('baz')), [])])])),
    ('foo.bar(baz, qux)',
     ns.Value(ns.Name(vl.Name('foo')), [
         ns.Field(vl.Name('bar')),
         ns.Call([ns.Value(ns.Name(vl.Name('baz')), []), ns.Value(ns.Name(vl.Name('qux')), [])])
     ])),
    ('foo.bar(baz, qux.quum())',
     ns.Value(ns.Name(vl.Name('foo')), [
         ns.Field(vl.Name('bar')),
         ns.Call([
             ns.Value(ns.Name(vl.Name('baz')), []),
             ns.Value(ns.Name(vl.Name('qux')), [ns.Field(vl.Name('quum')), ns.Call([])])
         ])
     ])),
    ('2.foo',
     ns.Value(ns.Number(vl.Number('2')), [ns.Field(vl.Name('foo'))])),
])
def test_expr(line: str, ast: AST):
    lexemes = lex_line(line)
    run_test('value', ast, lexemes, [], [])


@pytest.mark.parametrize('line,ast', [
    ('foo',
     ns.OpExpr(None, ns.Value(ns.Name(vl.Name('foo')), []), [], None)),
    ('++ foo',
     ns.OpExpr(vl.Operator('++'), ns.Value(ns.Name(vl.Name('foo')), []), [], None)),
    ('++ foo --',
     ns.OpExpr(vl.Operator('++'), ns.Value(ns.Name(vl.Name('foo')), []), [], vl.Operator('--'))),
    ('++ foo || bar --',
     ns.OpExpr(
         vl.Operator('++'),
         ns.Value(ns.Name(vl.Name('foo')), []),
         [ns.SubOpExpr(
             vl.Operator('||'),
             ns.Value(ns.Name(vl.Name('bar')), [])
         )],
         vl.Operator('--')
     )),
    ('++ foo ** bar || baz // qux',
     ns.OpExpr(
         vl.Operator('++'),
         ns.Value(ns.Name(vl.Name('foo')), []),
         [
             ns.SubOpExpr(vl.Operator('**'), ns.Value(ns.Name(vl.Name('bar')), [])),
             ns.SubOpExpr(vl.Operator('||'), ns.Value(ns.Name(vl.Name('baz')), [])),
             ns.SubOpExpr(vl.Operator('//'), ns.Value(ns.Name(vl.Name('qux')), []))
         ],
         None
     )),
])
def test_op_expr(line: str, ast: AST):
    lexemes = lex_line(line)
    run_test('op_expr', ast, lexemes, [], [])


@pytest.mark.parametrize('line,ast', [
    ('pass',
     ns.SimpleSuite(ns.SimpleStmt(ns.PassStmt()))),
    ('return',
     ns.SimpleSuite(ns.SimpleStmt(ns.ReturnStmt(ns.OpExprList([]))))),
    ('return foo',
     ns.SimpleSuite(ns.SimpleStmt(
         ns.ReturnStmt(ns.OpExprList([ns.OpExpr(None, ns.Value(ns.Name(vl.Name('foo')), []), [], None)]))))),
    ('return foo, ~bar, baz !',
     ns.SimpleSuite(ns.SimpleStmt(ns.ReturnStmt(ns.OpExprList([
         ns.OpExpr(None, ns.Value(ns.Name(vl.Name('foo')), []), [], None),
         ns.OpExpr(vl.Operator('~'), ns.Value(ns.Name(vl.Name('bar')), []), [], None),
         ns.OpExpr(None, ns.Value(ns.Name(vl.Name('baz')), []), [], vl.Operator('!'))
     ]))))),
])
def test_simple_suite(line: str, ast: AST):
    lexemes = lex_line(line)
    run_test('suite', ast, lexemes, [], [vl.NEWLINE])


@pytest.mark.parametrize('line,ast', [
    ('foo bar: Baz',
     ns.Parameter(vl.Name('foo'), vl.Name('bar'), vl.Class('Baz'))),
    ('bar: Baz',
     ns.Parameter(None, vl.Name('bar'), vl.Class('Baz'))),
])
def test_parameter(line: str, ast: AST):
    lexemes = lex_line(line)
    run_test('parameter', ast, lexemes, [], [])


@pytest.mark.parametrize('line,ast', [
    ('def foo() -> Bar: pass',
     ns.FuncDef(vl.Name('foo'), [], vl.Class('Bar'), ns.SimpleSuite(ns.SimpleStmt(ns.PassStmt())))),
    ('def foo(bar: Baz) -> Qux: pass',
     ns.FuncDef(vl.Name('foo'),
                [
                    ns.Parameter(None, vl.Name('bar'), vl.Class('Baz'))
                ],
                vl.Class('Qux'),
                ns.SimpleSuite(ns.SimpleStmt(ns.PassStmt())))),
    ('def foo(a b: C, d: E, f g: H) -> I: pass',
     ns.FuncDef(vl.Name('foo'),
                [
                    ns.Parameter(vl.Name('a'), vl.Name('b'), vl.Class('C')),
                    ns.Parameter(None, vl.Name('d'), vl.Class('E')),
                    ns.Parameter(vl.Name('f'), vl.Name('g'), vl.Class('H'))
                ],
                vl.Class('I'),
                ns.SimpleSuite(ns.SimpleStmt(ns.PassStmt())))),
])
def test_func_def(line: str, ast: AST):
    lexemes = lex_line(line)
    run_test('func_def', ast, lexemes, [], [vl.NEWLINE])


@pytest.mark.parametrize('line,ast', [
    ('class Foo: pass',
     ns.ClassDef(vl.Class('Foo'), None, ns.SimpleSuite(ns.SimpleStmt(ns.PassStmt())))),
])
def test_class_def(line: str, ast: AST):
    lexemes = lex_line(line)
    run_test('class_def', ast, lexemes, [], [vl.NEWLINE])
