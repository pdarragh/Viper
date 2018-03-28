import viper.parser as vg

from viper.lexer import lex_line
from viper.lexer.lexemes import *

from viper.parser.languages import (
    SPPF, ParseTreeChar as Char, ParseTreePair as Pair
)

import pytest


def char(x):
    return SPPF(Char(x))


def pair(x, y):
    return SPPF(Pair(x, y))


@pytest.mark.parametrize('line,sppf', [
    ('foo',
     char(Name('foo'))),
    ('42',
     char(Number('42'))),
    ('...',
     char(ELLIPSIS)),
    ('()',
     pair(char(OPEN_PAREN),
          char(CLOSE_PAREN))),
    ('(foo)',
     pair(char(OPEN_PAREN),
          pair(char(Name('foo')),
               char(CLOSE_PAREN)))),
])
def test_atom(line: str, sppf: SPPF):
    lexemes = lex_line(line)
    assert sppf == vg.GRAMMAR.parse_rule('atom', lexemes)


@pytest.mark.parametrize('line,sppf', [
    ('foo',
     char(Name('foo'))),
    ('foo.bar',
     pair(char(Name('foo')),
          pair(char(Period()),
               char(Name('bar'))))),
    ('foo.bar.baz',
     pair(char(Name('foo')),
          pair(pair(char(Period()),
                    char(Name('bar'))),
               pair(char(Period()),
                    char(Name('baz')))))),
    ('foo.bar(baz)',
     pair(char(Name('foo')),
          pair(pair(char(Period()),
                    char(Name('bar'))),
               pair(char(OPEN_PAREN),
                    pair(char(Name('baz')),
                         char(CLOSE_PAREN)))))),
    ('foo.bar(baz, qux)',
     pair(char(Name('foo')),
          pair(pair(char(Period()),
                    char(Name('bar'))),
               pair(char(OPEN_PAREN),
                    pair(pair(char(Name('baz')),
                              pair(char(Comma()),
                                   char(Name('qux')))),
                         char(CLOSE_PAREN)))))),
    ('2.foo',
     pair(char(Number('2')),
          pair(char(Period()),
               char(Name('foo'))))),
])
def test_expr(line: str, sppf: SPPF):
    lexemes = lex_line(line)
    assert sppf == vg.GRAMMAR.parse_rule('expr', lexemes)


@pytest.mark.parametrize('line,sppf', [
    ('()',
     pair(char(OPEN_PAREN),
          char(CLOSE_PAREN))),
    ('(foo: Bar)',
     pair(char(OPEN_PAREN),
          pair(pair(char(Name('foo')),
                    pair(char(COLON),
                         char(Class('Bar')))),
               char(CLOSE_PAREN)))),
    ('(foo bar: Baz)',
     pair(char(OPEN_PAREN),
          pair(pair(char(Name('foo')),
                    pair(char(Name('bar')),
                         pair(char(COLON),
                              char(Class('Baz'))))),
               char(CLOSE_PAREN)))),
])
def test_parameters(line: str, sppf: SPPF):
    lexemes = lex_line(line)
    assert sppf == vg.GRAMMAR.parse_rule('parameters', lexemes)


@pytest.mark.parametrize('line,sppf', [
    ('def foo() -> Bar: pass',
     pair(char(ReservedName('def')),
          pair(char(Name('foo')),
               pair(pair(char(OPEN_PAREN),
                         char(CLOSE_PAREN)),
                    pair(char(ARROW),
                         pair(char(Class('Bar')),
                              pair(char(COLON),
                                   pair(char(ReservedName('pass')),
                                        char(NEWLINE))))))))),
    ('def foo(a: B, c d: E) -> F: pass',
     pair(char(ReservedName('def')),
          pair(char(Name('foo')),
               pair(pair(char(OPEN_PAREN),
                         pair(pair(pair(char(Name('a')),
                                        pair(char(COLON),
                                             char(Class('B')))),
                                   pair(char(COMMA),
                                        pair(char(Name('c')),
                                             pair(char(Name('d')),
                                                  pair(char(COLON),
                                                       char(Class('E'))))))),
                              char(CLOSE_PAREN))),
                    pair(char(ARROW),
                         pair(char(Class('F')),
                              pair(char(COLON),
                                   pair(char(ReservedName('pass')),
                                        char(NEWLINE))))))))),
])
def test_func_def(line: str, sppf: SPPF):
    lexemes = lex_line(line)
    lexemes.append(NEWLINE)
    assert sppf == vg.GRAMMAR.parse_rule('func_def', lexemes)
