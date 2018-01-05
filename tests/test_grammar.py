import viper.grammar as vg
import viper.lexer as vl

from viper.grammar.languages import (
    SPPF,
    ParseTreeEmpty as PTE, ParseTreeChar as PTC, ParseTreePair as PTP, ParseTreeRep as PTR
)

import pytest


@pytest.mark.parametrize('line,sppf', [
    ('foo',
     SPPF(PTC(vl.Name('foo')))),
    ('42',
     SPPF(PTC(vl.Number('42')))),
    ('...',
     SPPF(PTC(vl.Operator('...')))),
    ('Zilch',
     SPPF(PTC(vl.Class('Zilch')))),
    ('True',
     SPPF(PTC(vl.Class('True')))),
    ('False',
     SPPF(PTC(vl.Class('False')))),
    ('()',
     SPPF(PTP(SPPF(PTC(vl.OpenParen())),
              SPPF(PTC(vl.CloseParen()))))),
    ('(foo)',
     SPPF(PTP(SPPF(PTC(vl.OpenParen())),
              SPPF(PTP(SPPF(PTP(SPPF(PTC(vl.Name('foo'))),
                                SPPF(PTR(SPPF())))),
                       SPPF(PTC(vl.CloseParen()))))))),
])
def test_atom(line: str, sppf: SPPF):
    atom = vg.GRAMMAR.get_rule('atom')
    lexemes = vl.lex_line(line)
    assert sppf == vg.make_sppf(atom, lexemes)
