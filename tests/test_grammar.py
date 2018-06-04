from viper.lexer import lex_line, lex_lines
from viper.parser import *
from viper.parser.ast.ast_to_string import ast_to_string

import viper.lexer as vl
import viper.parser.ast.nodes as ns

import pytest

from typing import List


def run_test(rule: str, tree: AST, lexemes: List[vl.Lexeme], prepend: List[vl.Lexeme], append: List[vl.Lexeme]):
    parse = GRAMMAR.parse_rule(rule, prepend + lexemes + append)
    try:
        assert isinstance(parse, SingleParse)
    except AssertionError:
        print(f"lexemes: {lexemes}")
        print(f"parse: {parse}")
        print(f"ast: {tree}")
        print(f"rule: {rule}")
        raise
    try:
        assert tree == parse.ast
    except AssertionError:
        print(f"Got AST:\n{ast_to_string(parse.ast)}")
        print()
        print(f"Wanted AST:\n{ast_to_string(tree)}")
        raise


@pytest.mark.parametrize('line,tree', [
    ('foo',
     ns.NameAtom(vl.Name('foo'))),
    ('42',
     ns.NumberAtom(vl.Number('42'))),
    ('...',
     ns.EllipsisAtom()),
    ('()',
     ns.ParenAtom(None)),
    ('(foo)',
     ns.ParenAtom(ns.TestExprList([ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
         ns.OpExpr(None, ns.AtomExpr(ns.NameAtom(vl.Name('foo')), []), [], None)])])]))]))),
])
def test_atom(line: str, tree: AST):
    lexemes = lex_line(line)
    run_test('atom', tree, lexemes, [], [])


@pytest.mark.parametrize('line,tree', [
    ('foo',
     ns.AtomExpr(ns.NameAtom(vl.Name('foo')), [])),
    ('foo.bar',
     ns.AtomExpr(ns.NameAtom(vl.Name('foo')), [ns.Field(vl.Name('bar'))])),
    ('foo.bar.baz',
     ns.AtomExpr(ns.NameAtom(vl.Name('foo')), [ns.Field(vl.Name('bar')), ns.Field(vl.Name('baz'))])),
    ('foo.bar(baz)',
     ns.AtomExpr(ns.NameAtom(vl.Name('foo')), [ns.Field(vl.Name('bar')),
                                               ns.Call([ns.AtomExpr(ns.NameAtom(vl.Name('baz')), [])])])),
    ('foo.bar(baz, qux)',
     ns.AtomExpr(ns.NameAtom(vl.Name('foo')), [
         ns.Field(vl.Name('bar')),
         ns.Call([ns.AtomExpr(ns.NameAtom(vl.Name('baz')), []), ns.AtomExpr(ns.NameAtom(vl.Name('qux')), [])])
     ])),
    ('foo.bar(baz, qux.quum())',
     ns.AtomExpr(ns.NameAtom(vl.Name('foo')), [
         ns.Field(vl.Name('bar')),
         ns.Call([
             ns.AtomExpr(ns.NameAtom(vl.Name('baz')), []),
             ns.AtomExpr(ns.NameAtom(vl.Name('qux')), [ns.Field(vl.Name('quum')), ns.Call([])])
         ])
     ])),
    ('2.foo',
     ns.AtomExpr(ns.NumberAtom(vl.Number('2')), [ns.Field(vl.Name('foo'))])),
])
def test_expr(line: str, tree: AST):
    lexemes = lex_line(line)
    run_test('atom_expr', tree, lexemes, [], [])


@pytest.mark.parametrize('line,tree', [
    ('foo',
     ns.OpExpr(None, ns.AtomExpr(ns.NameAtom(vl.Name('foo')), []), [], None)),
    ('++ foo',
     ns.OpExpr(vl.Operator('++'), ns.AtomExpr(ns.NameAtom(vl.Name('foo')), []), [], None)),
    ('++ foo --',
     ns.OpExpr(vl.Operator('++'), ns.AtomExpr(ns.NameAtom(vl.Name('foo')), []), [], vl.Operator('--'))),
    ('++ foo || bar --',
     ns.OpExpr(
         vl.Operator('++'),
         ns.AtomExpr(ns.NameAtom(vl.Name('foo')), []),
         [ns.SubOpExpr(
             vl.Operator('||'),
             ns.AtomExpr(ns.NameAtom(vl.Name('bar')), [])
         )],
         vl.Operator('--')
     )),
    ('++ foo ** bar || baz // qux',
     ns.OpExpr(
         vl.Operator('++'),
         ns.AtomExpr(ns.NameAtom(vl.Name('foo')), []),
         [
             ns.SubOpExpr(vl.Operator('**'), ns.AtomExpr(ns.NameAtom(vl.Name('bar')), [])),
             ns.SubOpExpr(vl.Operator('||'), ns.AtomExpr(ns.NameAtom(vl.Name('baz')), [])),
             ns.SubOpExpr(vl.Operator('//'), ns.AtomExpr(ns.NameAtom(vl.Name('qux')), []))
         ],
         None
     )),
])
def test_op_expr(line: str, tree: AST):
    lexemes = lex_line(line)
    run_test('op_expr', tree, lexemes, [], [])


@pytest.mark.parametrize('line,tree', [
    ('pass',
     ns.SimpleStmtBlock(ns.SimpleStmt(ns.EmptyStmt()))),
    ('return',
     ns.SimpleStmtBlock(ns.SimpleStmt(ns.ReturnStmt(None)))),
    ('return foo',
     ns.SimpleStmtBlock(
         ns.SimpleStmt(ns.ReturnStmt(ns.TestExprList([ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
             ns.OpExpr(None,
                       ns.AtomExpr(ns.NameAtom(vl.Name('foo')), []),
                       [],
                       None)])])]))]))))),
    ('return foo, ~bar, baz !',
     ns.SimpleStmtBlock(
         ns.SimpleStmt(ns.ReturnStmt(ns.TestExprList([
             ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                 ns.OpExpr(None,
                           ns.AtomExpr(ns.NameAtom(vl.Name('foo')), []),
                           [],
                           None)])])])),
             ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                 ns.OpExpr(vl.Operator('~'),
                           ns.AtomExpr(ns.NameAtom(vl.Name('bar')), []),
                           [],
                           None)])])])),
             ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                 ns.OpExpr(None,
                           ns.AtomExpr(ns.NameAtom(vl.Name('baz')), []),
                           [],
                           vl.Operator('!'))])])]))]))))),
])
def test_stmt_block(line: str, tree: AST):
    lexemes = lex_line(line)
    run_test('stmt_block', tree, lexemes, [], [vl.NEWLINE])


@pytest.mark.parametrize('line,tree', [
    ('foo bar: Baz',
     ns.Parameter(vl.Name('foo'), vl.Name('bar'), vl.Class('Baz'))),
    ('bar: Baz',
     ns.Parameter(None, vl.Name('bar'), vl.Class('Baz'))),
])
def test_parameter(line: str, tree: AST):
    lexemes = lex_line(line)
    run_test('parameter', tree, lexemes, [], [])


@pytest.mark.parametrize('line,tree', [
    ('def foo() -> Bar: pass',
     ns.FuncDef(vl.Name('foo'), [], vl.Class('Bar'), ns.SimpleStmtBlock(ns.SimpleStmt(ns.EmptyStmt())))),
    ('def foo(bar: Baz) -> Qux: pass',
     ns.FuncDef(vl.Name('foo'),
                [
                    ns.Parameter(None, vl.Name('bar'), vl.Class('Baz'))
                ],
                vl.Class('Qux'),
                ns.SimpleStmtBlock(ns.SimpleStmt(ns.EmptyStmt())))),
    ('def foo(a b: C, d: E, f g: H) -> I: pass',
     ns.FuncDef(vl.Name('foo'),
                [
                    ns.Parameter(vl.Name('a'), vl.Name('b'), vl.Class('C')),
                    ns.Parameter(None, vl.Name('d'), vl.Class('E')),
                    ns.Parameter(vl.Name('f'), vl.Name('g'), vl.Class('H'))
                ],
                vl.Class('I'),
                ns.SimpleStmtBlock(ns.SimpleStmt(ns.EmptyStmt())))),
])
def test_func_def(line: str, tree: AST):
    lexemes = lex_line(line)
    run_test('func_def', tree, lexemes, [], [vl.NEWLINE])


@pytest.mark.parametrize('line,tree', [
    ('class Foo: pass',
     ns.ClassDef(vl.Class('Foo'), None, ns.SimpleStmtBlock(ns.SimpleStmt(ns.EmptyStmt())))),
])
def test_class_def(line: str, tree: AST):
    lexemes = lex_line(line)
    run_test('class_def', tree, lexemes, [], [vl.NEWLINE])


@pytest.mark.parametrize('lines,tree', [
    ([
         'if x == y:',
         '    return 42'
     ],
     ns.IfStmt(
         ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
             ns.OpExpr(None,
                       ns.AtomExpr(ns.NameAtom(vl.Name('x')), []),
                       [ns.SubOpExpr(vl.Operator('=='),
                                     ns.AtomExpr(ns.NameAtom(vl.Name('y')), []))],
                       None)])])])),
         ns.CompoundStmtBlock(
             [ns.SimpleStmt(ns.ReturnStmt(ns.TestExprList([ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                 ns.OpExpr(None,
                           ns.AtomExpr(ns.NumberAtom(vl.Number('42')), []),
                           [],
                           None)])])]))])))]),
         [],
         None)),
    ([
         'if x == y:',
         '    if x == z:',
         '        return 42'
     ],
     ns.IfStmt(
         ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
             ns.OpExpr(None,
                       ns.AtomExpr(ns.NameAtom(vl.Name('x')), []),
                       [ns.SubOpExpr(vl.Operator('=='),
                                     ns.AtomExpr(ns.NameAtom(vl.Name('y')), []))],
                       None)])])])),
         ns.CompoundStmtBlock([
             ns.IfStmt(
                 ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                     ns.OpExpr(None,
                               ns.AtomExpr(ns.NameAtom(vl.Name('x')), []),
                               [ns.SubOpExpr(vl.Operator('=='),
                                             ns.AtomExpr(ns.NameAtom(vl.Name('z')), []))],
                               None)])])])),
                 ns.CompoundStmtBlock([ns.SimpleStmt(
                     ns.ReturnStmt(ns.TestExprList([ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                         ns.OpExpr(None,
                                   ns.AtomExpr(ns.NumberAtom(vl.Number('42')), []),
                                   [],
                                   None)])])]))])))]),
                 [],
                 None)]),
         [],
         None)),
    ([
         'if x == y:',
         '    pass',
         'else:',
         '    return 42'
     ],
     ns.IfStmt(
         ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
             ns.OpExpr(None,
                       ns.AtomExpr(ns.NameAtom(vl.Name('x')), []),
                       [ns.SubOpExpr(vl.Operator('=='),
                                     ns.AtomExpr(ns.NameAtom(vl.Name('y')), []))],
                       None)])])])),
         ns.CompoundStmtBlock([ns.SimpleStmt(ns.EmptyStmt())]),
         [],
         ns.ElseStmt(ns.CompoundStmtBlock(
             [ns.SimpleStmt(ns.ReturnStmt(ns.TestExprList([ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                 ns.OpExpr(None,
                           ns.AtomExpr(ns.NumberAtom(vl.Number('42')), []),
                           [],
                           None)])])]))])))])))),
    ([
         'if x == y: pass',
         'else:',
         '    return 42'
     ],
     ns.IfStmt(
         ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
             ns.OpExpr(None,
                       ns.AtomExpr(ns.NameAtom(vl.Name('x')), []),
                       [ns.SubOpExpr(vl.Operator('=='),
                                     ns.AtomExpr(ns.NameAtom(vl.Name('y')), []))],
                       None)])])])),
         ns.SimpleStmtBlock(ns.SimpleStmt(ns.EmptyStmt())),
         [],
         ns.ElseStmt(ns.CompoundStmtBlock(
             [ns.SimpleStmt(ns.ReturnStmt(ns.TestExprList([ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                 ns.OpExpr(None,
                           ns.AtomExpr(ns.NumberAtom(vl.Number('42')), []),
                           [],
                           None)])])]))])))])))),
    ([
         'if x == y: pass',
         'else: return 42'
     ],
     ns.IfStmt(
         ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
             ns.OpExpr(None,
                       ns.AtomExpr(ns.NameAtom(vl.Name('x')), []),
                       [ns.SubOpExpr(vl.Operator('=='),
                                     ns.AtomExpr(ns.NameAtom(vl.Name('y')), []))],
                       None)])])])),
         ns.SimpleStmtBlock(ns.SimpleStmt(ns.EmptyStmt())),
         [],
         ns.ElseStmt(ns.SimpleStmtBlock(
             ns.SimpleStmt(ns.ReturnStmt(ns.TestExprList([ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                 ns.OpExpr(None,
                           ns.AtomExpr(ns.NumberAtom(vl.Number('42')), []),
                           [],
                           None)])])]))]))))))),
])
def test_if_stmt(lines: List[str], tree: AST):
    lexemes = lex_lines('\n'.join(lines))[:-1]
    run_test('if_stmt', tree, lexemes, [], [])


@pytest.mark.parametrize('lines,tree', [
    ([
         'if x == y:',
         '    42'
     ],
     ns.IfExpr(
         ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
             ns.OpExpr(None,
                       ns.AtomExpr(ns.NameAtom(vl.Name('x')), []),
                       [ns.SubOpExpr(vl.Operator('=='),
                                     ns.AtomExpr(ns.NameAtom(vl.Name('y')), []))],
                       None)])])])),
         ns.IndentedExprBlock(ns.TestExprList([ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
             ns.OpExpr(None,
                       ns.AtomExpr(ns.NumberAtom(vl.Number('42')), []),
                       [],
                       None)])])]))])),
         [],
         None)),
    ([
         'if x == y: 42'
     ],
     ns.IfExpr(
         ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
             ns.OpExpr(None,
                       ns.AtomExpr(ns.NameAtom(vl.Name('x')), []),
                       [ns.SubOpExpr(vl.Operator('=='),
                                     ns.AtomExpr(ns.NameAtom(vl.Name('y')), []))],
                       None)])])])),
         ns.SimpleExprBlock(ns.TestExprList([ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
             ns.OpExpr(None,
                       ns.AtomExpr(ns.NumberAtom(vl.Number('42')), []),
                       [],
                       None)])])]))])),
         [],
         None)),
])
def test_if_expr(lines: List[str], tree: AST):
    lexemes = lex_lines('\n'.join(lines))[:-1]
    run_test('if_expr', tree, lexemes, [], [])


@pytest.mark.parametrize('lines,tree', [
    ([
         'z = if x == y:',
         '    42'
     ],
     ns.AssignStmt(
         vl.Name('z'),
         ns.IfExpr(
             ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                 ns.OpExpr(None,
                           ns.AtomExpr(ns.NameAtom(vl.Name('x')), []),
                           [ns.SubOpExpr(vl.Operator('=='),
                                         ns.AtomExpr(ns.NameAtom(vl.Name('y')), []))],
                           None)])])])),
             ns.IndentedExprBlock(ns.TestExprList([ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                 ns.OpExpr(None,
                           ns.AtomExpr(ns.NumberAtom(vl.Number('42')), []),
                           [],
                           None)])])]))])),
             [],
             None))),
    ([
         'z = if x == y: 42'
     ],
     ns.AssignStmt(
         vl.Name('z'),
         ns.IfExpr(
             ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                 ns.OpExpr(None,
                           ns.AtomExpr(ns.NameAtom(vl.Name('x')), []),
                           [ns.SubOpExpr(vl.Operator('=='),
                                         ns.AtomExpr(ns.NameAtom(vl.Name('y')), []))],
                           None)])])])),
             ns.SimpleExprBlock(ns.TestExprList([ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                 ns.OpExpr(None,
                           ns.AtomExpr(ns.NumberAtom(vl.Number('42')), []),
                           [],
                           None)])])]))])),
             [],
             None))),
    ([
         'z = if x == y:',
         '    42',
         'elif x > y:',
         '    19',
         'elif x < 0: 2',
         'else:',
         '    13'
     ],
     ns.AssignStmt(
         vl.Name('z'),
         ns.IfExpr(
             ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                 ns.OpExpr(None,
                           ns.AtomExpr(ns.NameAtom(vl.Name('x')), []),
                           [ns.SubOpExpr(vl.Operator('=='),
                                         ns.AtomExpr(ns.NameAtom(vl.Name('y')), []))],
                           None)])])])),
             ns.IndentedExprBlock(ns.TestExprList([ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                 ns.OpExpr(None,
                           ns.AtomExpr(ns.NumberAtom(vl.Number('42')), []),
                           [],
                           None)])])]))])),
             [ns.ElifExpr(
                 ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                     ns.OpExpr(None,
                               ns.AtomExpr(ns.NameAtom(vl.Name('x')), []),
                               [ns.SubOpExpr(vl.Operator('>'),
                                             ns.AtomExpr(ns.NameAtom(vl.Name('y')), []))],
                               None)])])])),
                 ns.IndentedExprBlock(ns.TestExprList([ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                     ns.OpExpr(None,
                               ns.AtomExpr(ns.NumberAtom(vl.Number('19')), []),
                               [],
                               None)])])]))]))),
                 ns.ElifExpr(
                     ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                         ns.OpExpr(None,
                                   ns.AtomExpr(ns.NameAtom(vl.Name('x')), []),
                                   [ns.SubOpExpr(vl.Operator('<'),
                                                 ns.AtomExpr(ns.NumberAtom(vl.Number('0')), []))],
                                   None)])])])),
                     ns.SimpleExprBlock(ns.TestExprList([ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                         ns.OpExpr(None,
                                   ns.AtomExpr(ns.NumberAtom(vl.Number('2')), []),
                                   [],
                                   None)])])]))])))],
             ns.ElseExpr(
                 ns.IndentedExprBlock(ns.TestExprList([ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                     ns.OpExpr(None,
                               ns.AtomExpr(ns.NumberAtom(vl.Number('13')), []),
                               [],
                               None)])])]))])))))),
])
def test_assign_stmt(lines: List[str], tree: AST):
    lexemes = lex_lines('\n'.join(lines))[:-1]
    run_test('assign_stmt', tree, lexemes, [], [])


# TODO: NAME cannot include '_' if I want them to be handled in the patterns like this.
@pytest.mark.parametrize('line,tree', [
    ('x: Int',
     ns.NamedPattern(vl.Name('x'), vl.Class('Int'))),
    ('_: Int',
     ns.NamelessPattern(vl.Class('Int'))),
    ('x',
     ns.SimpleNamedPattern(vl.Name('x'))),
    ('_',
     ns.SimpleNamelessPattern()),
    ('(x: Foo, y: Bar)',
     ns.SimpleParenPattern(ns.PatternList([
         ns.NamedPattern(vl.Name('x'), vl.Class('Foo')),
         ns.NamedPattern(vl.Name('y'), vl.Class('Bar'))]))),
    ('(_: Foo, y: Bar)',
     ns.SimpleParenPattern(ns.PatternList([
         ns.NamelessPattern(vl.Class('Foo')),
         ns.NamedPattern(vl.Name('y'), vl.Class('Bar'))]))),
])
def test_pattern(line: str, tree: AST):
    lexemes = lex_line(line)
    run_test('pattern', tree, lexemes, [], [])
