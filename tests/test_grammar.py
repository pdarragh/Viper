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
               SPPF(Pair(SPPF(Pair(SPPF(Char(vl.Name('foo'))),
                                   SPPF(Repeat(SPPF())))),
                         SPPF(Char(vl.CloseParen()))))))),
])
def test_atom(line: str, sppf: SPPF):
    atom = vg.GRAMMAR.get_rule('atom')
    lexemes = vl.lex_line(line)
    assert sppf == vg.make_sppf(atom, lexemes)


@pytest.mark.parametrize('line,sppf', [
    ('foo',
     SPPF(Pair(SPPF(Char(vl.Name('foo'))),
               SPPF(Repeat(SPPF()))))),
    ('foo.bar',
     SPPF(Pair(SPPF(Char(vl.Name('foo'))),
               SPPF(Pair(SPPF(Pair(SPPF(Char(vl.Period())),
                                   SPPF(Char(vl.Name('bar'))))),
                         SPPF(Repeat(SPPF()))))))),
    ('foo.bar.baz',
     SPPF(Pair(SPPF(Char(vl.Name('foo'))),
               SPPF(Pair(SPPF(Pair(SPPF(Char(vl.Period())),
                                   SPPF(Char(vl.Name('bar'))))),
                         SPPF(Pair(SPPF(Pair(SPPF(Char(vl.Period())),
                                             SPPF(Char(vl.Name('baz'))))),
                                   SPPF(Repeat(SPPF()))))))))),
    ('foo.bar(baz)',
     SPPF(Pair(SPPF(Char(vl.Name('foo'))),
               SPPF(Pair(SPPF(Pair(SPPF(Char(vl.Period())),
                                   SPPF(Char(vl.Name('bar'))))),
                         SPPF(Pair(SPPF(Pair(SPPF(Char(vl.OpenParen())),
                                             SPPF(Pair(SPPF(Pair(SPPF(Char(vl.Name('baz'))),
                                                                 SPPF(Repeat(SPPF())))),
                                                       SPPF(Char(vl.CloseParen())))))),
                                   SPPF(Repeat(SPPF()))))))))),
    ('foo.bar(baz, qux)',
     SPPF(Pair(SPPF(Char(vl.Name('foo'))),
               SPPF(Pair(SPPF(Pair(SPPF(Char(vl.Period())),
                                   SPPF(Char(vl.Name('bar'))))),
                         SPPF(Pair(SPPF(Pair(SPPF(Char(vl.OpenParen())),
                                             SPPF(Pair(SPPF(Pair(SPPF(Pair(SPPF(Char(vl.Name('baz'))),
                                                                           SPPF(Repeat(SPPF())))),
                                                                 SPPF(Pair(SPPF(Char(vl.Comma())),
                                                                           SPPF(Pair(SPPF(Char(vl.Name('qux'))),
                                                                                     SPPF(Repeat(SPPF())))))))),
                                                       SPPF(Char(vl.CloseParen())))))),
                                   SPPF(Repeat(SPPF()))))))))),
    ('2.foo',
     SPPF(Pair(SPPF(Char(vl.Number('2'))),
               SPPF(Pair(SPPF(Pair(SPPF(Char(vl.Period())),
                                   SPPF(Char(vl.Name('foo'))))),
                         SPPF(Repeat(SPPF()))))))),
])
def test_expr(line: str, sppf: SPPF):
    expr = vg.GRAMMAR.get_rule('expr')
    lexemes = vl.lex_line(line)
    assert sppf == vg.make_sppf(expr, lexemes)
