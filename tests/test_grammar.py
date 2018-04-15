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
