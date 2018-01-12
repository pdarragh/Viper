import viper.grammar as vg
import viper.lexer as vl

from viper.grammar.languages import (
    SPPF,
    ParseTreeEmpty as Empty, ParseTreeChar as Char, ParseTreePair as Pair, ParseTreeRep as Repeat
)

import pytest


@pytest.mark.parametrize('line,sppf', [
    ('foo',
     SPPF(Char(vl.Name('foo')))),
    ('42',
     SPPF(Char(vl.Number('42')))),
    ('...',
     SPPF(Char(vl.Operator('...')))),
    ('Zilch',
     SPPF(Char(vl.Class('Zilch')))),
    ('True',
     SPPF(Char(vl.Class('True')))),
    ('False',
     SPPF(Char(vl.Class('False')))),
    ('()',
     SPPF(Pair(SPPF(Char(vl.OpenParen())),
               SPPF(Char(vl.CloseParen()))))),
    ('(foo)',
     SPPF(Pair(SPPF(Char(vl.OpenParen())),
               SPPF(Pair(SPPF(Char(vl.Name('foo'))),
                         SPPF(Char(vl.CloseParen()))))))),
])
def test_atom(line: str, sppf: SPPF):
    lexemes = vl.lex_line(line)
    assert sppf == vg.GRAMMAR.parse_rule('atom', lexemes)


@pytest.mark.parametrize('line,sppf', [
    ('foo',
     SPPF(Char(vl.Name('foo')))),
    ('foo.bar',
     SPPF(Pair(SPPF(Char(vl.Name('foo'))),
               SPPF(Pair(SPPF(Char(vl.Period())),
                         SPPF(Char(vl.Name('bar')))))))),
    ('foo.bar.baz',
     SPPF(Pair(SPPF(Char(vl.Name('foo'))),
               SPPF(Pair(SPPF(Pair(SPPF(Char(vl.Period())),
                                   SPPF(Char(vl.Name('bar'))))),
                         SPPF(Pair(SPPF(Char(vl.Period())),
                                   SPPF(Char(vl.Name('baz')))))))))),
    ('foo.bar(baz)',
     SPPF(Pair(SPPF(Char(vl.Name('foo'))),
               SPPF(Pair(SPPF(Pair(SPPF(Char(vl.Period())),
                                   SPPF(Char(vl.Name('bar'))))),
                         SPPF(Pair(SPPF(Char(vl.OpenParen())),
                                   SPPF(Pair(SPPF(Char(vl.Name('baz'))),
                                             SPPF(Char(vl.CloseParen()))))))))))),
    ('foo.bar(baz, qux)',
     SPPF(Pair(SPPF(Char(vl.Name('foo'))),
               SPPF(Pair(SPPF(Pair(SPPF(Char(vl.Period())),
                                   SPPF(Char(vl.Name('bar'))))),
                         SPPF(Pair(SPPF(Char(vl.OpenParen())),
                                   SPPF(Pair(SPPF(Pair(SPPF(Char(vl.Name('baz'))),
                                                       SPPF(Pair(SPPF(Char(vl.Comma())),
                                                                 SPPF(Char(vl.Name('qux'))))))),
                                             SPPF(Char(vl.CloseParen()))))))))))),
    ('2.foo',
     SPPF(Pair(SPPF(Char(vl.Number('2'))),
               SPPF(Pair(SPPF(Char(vl.Period())),
                         SPPF(Char(vl.Name('foo')))))))),
])
def test_expr(line: str, sppf: SPPF):
    lexemes = vl.lex_line(line)
    assert sppf == vg.GRAMMAR.parse_rule('expr', lexemes)


@pytest.mark.parametrize('line,sppf', [
    ('()',
     SPPF(Pair(SPPF(Char(vl.OPEN_PAREN)),
               SPPF(Char(vl.CLOSE_PAREN))))),
    ('(foo: Bar)',
     SPPF(Pair(SPPF(Char(vl.OPEN_PAREN)),
               SPPF(Pair(SPPF(Pair(SPPF(Char(vl.Name('foo'))),
                                   SPPF(Pair(SPPF(Char(vl.COLON)),
                                             SPPF(Char(vl.Class('Bar'))))))),
                         SPPF(Char(vl.CLOSE_PAREN))))))),
    ('(foo bar: Baz)',
     SPPF(Pair(SPPF(Char(vl.OPEN_PAREN)),
               SPPF(Pair(SPPF(Pair(SPPF(Char(vl.Name('foo'))),
                                   SPPF(Pair(SPPF(Char(vl.Name('bar'))),
                                             SPPF(Pair(SPPF(Char(vl.COLON)),
                                                       SPPF(Char(vl.Class('Baz'))))))))),
                         SPPF(Char(vl.CLOSE_PAREN))))))),
])
def test_parameters(line: str, sppf: SPPF):
    lexemes = vl.lex_line(line)
    assert sppf == vg.GRAMMAR.parse_rule('parameters', lexemes)


@pytest.mark.parametrize('line,sppf', [
    ('def foo() -> Bar: pass',
     SPPF(Pair(SPPF(Char(vl.Name('def'))),
               SPPF(Pair(SPPF(Char(vl.Name('foo'))),
                         SPPF(Pair(SPPF(Pair(SPPF(Char(vl.OPEN_PAREN)),
                                             SPPF(Char(vl.CLOSE_PAREN)))),
                                   SPPF(Pair(SPPF(Char(vl.ARROW)),
                                             SPPF(Pair(SPPF(Char(vl.Class('Bar'))),
                                                       SPPF(Pair(SPPF(Char(vl.COLON)),
                                                                 SPPF(Pair(SPPF(Char(vl.Name('pass'))),
                                                                           SPPF(Char(vl.NEWLINE))))))))))))))))),
    ('def foo(a: B, c d: E) -> F: pass',
     SPPF(Pair(SPPF(Char(vl.Name('def'))),
               SPPF(Pair(SPPF(Char(vl.Name('foo'))),
                         SPPF(Pair(SPPF(Pair(SPPF(Char(vl.OPEN_PAREN)),
                                             SPPF(Pair(SPPF(Pair(SPPF(Pair(SPPF(Char(vl.Name('a'))),
                                                                           SPPF(Pair(SPPF(Char(vl.COLON)),
                                                                                     SPPF(Char(vl.Class('B'))))))),
                                                                 SPPF(Pair(SPPF(Char(vl.COMMA)),
                                                                           SPPF(Pair(SPPF(Char(vl.Name('c'))),
                                                                                     SPPF(Pair(SPPF(Char(vl.Name('d'))),
                                                                                               SPPF(Pair(SPPF(Char(vl.COLON)),
                                                                                                         SPPF(Char(vl.Class('E'))))))))))))),
                                                       SPPF(Char(vl.CLOSE_PAREN)))))),
                                   SPPF(Pair(SPPF(Char(vl.ARROW)),
                                             SPPF(Pair(SPPF(Char(vl.Class('F'))),
                                                       SPPF(Pair(SPPF(Char(vl.COLON)),
                                                                 SPPF(Pair(SPPF(Char(vl.Name('pass'))),
                                                                           SPPF(Char(vl.NEWLINE))))))))))))))))),
])
def test_func_def(line: str, sppf: SPPF):
    lexemes = vl.lex_line(line)
    lexemes.append(vl.NEWLINE)
    assert sppf == vg.GRAMMAR.parse_rule('func_def', lexemes)
