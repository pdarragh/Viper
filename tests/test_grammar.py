import viper.grammar as vg
import viper.grammar.languages as vgl
import viper.lexer as vl

import pytest


@pytest.mark.parametrize('line,sppf', [
    ('foo',
     vgl.SPPF(vgl.ParseTreeChar(vl.Name('foo')))),
    ('2',
     vgl.SPPF(vgl.ParseTreeChar(vl.Number('2')))),
    ('...',
     vgl.SPPF(vgl.ParseTreeChar(vl.Operator('...')))),
    ('Zilch',
     vgl.SPPF(vgl.ParseTreeChar(vl.Class('Zilch')))),
    ('True',
     vgl.SPPF(vgl.ParseTreeChar(vl.Class('True')))),
    ('False',
     vgl.SPPF(vgl.ParseTreeChar(vl.Class('False')))),
])
def test_atom(line: str, sppf: vgl.SPPF):
    atom = vg.GRAMMAR.get_rule('atom')
    lexemes = vl.lex_line(line)
    assert sppf == vg.make_sppf(atom, lexemes)
