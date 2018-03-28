from .languages import SPPF, make_sppf
from .linguify_grammar import linguify_grammar_file

from viper.lexer import Lexeme

from os.path import join, dirname
from typing import List


class Grammar:
    def __init__(self, grammar_filename: str):
        self.file = grammar_filename
        self.rules = linguify_grammar_file(self.file)

    def parse_rule(self, rule: str, lexemes: List[Lexeme]) -> SPPF:
        lang = self.rules[rule]
        return make_sppf(lang, lexemes)


GRAMMAR_FILE = join(dirname(__file__), join('grammar_parsing', 'formal_grammar.bnf'))
GRAMMAR = Grammar(GRAMMAR_FILE)
