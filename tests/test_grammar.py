import viper.grammar as vg
import viper.lexer as vl

from viper.grammar.languages import (
    SPPF,
    ParseTreeEmpty as Empty, ParseTreeChar as Char, ParseTreePair as Pair, ParseTreeRep as Repeat
)

import pytest


def char(x):
    return SPPF(Char(x))


def pair(x, y):
    return SPPF(Pair(x, y))


@pytest.mark.parametrize('line,sppf', [
    ('foo',
     char(vl.Name('foo'))),
    ('42',
     char(vl.Number('42'))),
    ('...',
     char(vl.Operator('...'))),
    ('Zilch',
     char(vl.Class('Zilch'))),
    ('True',
     char(vl.Class('True'))),
    ('False',
     char(vl.Class('False'))),
    ('()',
     pair(char(vl.OpenParen()),
          char(vl.CloseParen()))),
    ('(foo)',
     pair(char(vl.OpenParen()),
          pair(char(vl.Name('foo')),
               char(vl.CloseParen())))),
])
def test_atom(line: str, sppf: SPPF):
    lexemes = vl.lex_line(line)
    assert sppf == vg.GRAMMAR.parse_rule('atom', lexemes)


@pytest.mark.parametrize('line,sppf', [
    ('foo',
     char(vl.Name('foo'))),
    ('foo.bar',
     pair(char(vl.Name('foo')),
          pair(char(vl.Period()),
               char(vl.Name('bar'))))),
    ('foo.bar.baz',
     pair(char(vl.Name('foo')),
          pair(pair(char(vl.Period()),
                    char(vl.Name('bar'))),
               pair(char(vl.Period()),
                    char(vl.Name('baz')))))),
    ('foo.bar(baz)',
     pair(char(vl.Name('foo')),
          pair(pair(char(vl.Period()),
                    char(vl.Name('bar'))),
               pair(char(vl.OpenParen()),
                    pair(char(vl.Name('baz')),
                         char(vl.CloseParen())))))),
    ('foo.bar(baz, qux)',
     pair(char(vl.Name('foo')),
          pair(pair(char(vl.Period()),
                    char(vl.Name('bar'))),
               pair(char(vl.OpenParen()),
                    pair(pair(char(vl.Name('baz')),
                              pair(char(vl.Comma()),
                                   char(vl.Name('qux')))),
                         char(vl.CloseParen())))))),
    ('2.foo',
     pair(char(vl.Number('2')),
          pair(char(vl.Period()),
               char(vl.Name('foo'))))),
])
def test_expr(line: str, sppf: SPPF):
    lexemes = vl.lex_line(line)
    assert sppf == vg.GRAMMAR.parse_rule('expr', lexemes)


@pytest.mark.parametrize('line,sppf', [
    ('()',
     pair(char(vl.OPEN_PAREN),
          char(vl.CLOSE_PAREN))),
    ('(foo: Bar)',
     pair(char(vl.OPEN_PAREN),
          pair(pair(char(vl.Name('foo')),
                    pair(char(vl.COLON),
                         char(vl.Class('Bar')))),
               char(vl.CLOSE_PAREN)))),
    ('(foo bar: Baz)',
     pair(char(vl.OPEN_PAREN),
          pair(pair(char(vl.Name('foo')),
                    pair(char(vl.Name('bar')),
                         pair(char(vl.COLON),
                              char(vl.Class('Baz'))))),
               char(vl.CLOSE_PAREN)))),
])
def test_parameters(line: str, sppf: SPPF):
    lexemes = vl.lex_line(line)
    assert sppf == vg.GRAMMAR.parse_rule('parameters', lexemes)


@pytest.mark.parametrize('line,sppf', [
    ('def foo() -> Bar: pass',
     pair(char(vl.Name('def')),
          pair(char(vl.Name('foo')),
               pair(pair(char(vl.OPEN_PAREN),
                         char(vl.CLOSE_PAREN)),
                    pair(char(vl.ARROW),
                         pair(char(vl.Class('Bar')),
                              pair(char(vl.COLON),
                                   pair(char(vl.Name('pass')),
                                        char(vl.NEWLINE))))))))),
    ('def foo(a: B, c d: E) -> F: pass',
     pair(char(vl.Name('def')),
          pair(char(vl.Name('foo')),
               pair(pair(char(vl.OPEN_PAREN),
                         pair(pair(pair(char(vl.Name('a')),
                                        pair(char(vl.COLON),
                                             char(vl.Class('B')))),
                                   pair(char(vl.COMMA),
                                        pair(char(vl.Name('c')),
                                             pair(char(vl.Name('d')),
                                                  pair(char(vl.COLON),
                                                       char(vl.Class('E'))))))),
                              char(vl.CLOSE_PAREN))),
                    pair(char(vl.ARROW),
                         pair(char(vl.Class('F')),
                              pair(char(vl.COLON),
                                   pair(char(vl.Name('pass')),
                                        char(vl.NEWLINE))))))))),
])
def test_func_def(line: str, sppf: SPPF):
    lexemes = vl.lex_line(line)
    lexemes.append(vl.NEWLINE)
    assert sppf == vg.GRAMMAR.parse_rule('func_def', lexemes)
