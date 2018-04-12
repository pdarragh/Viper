from .ast.nodes import AST
from .languages import ParseTreeChar, make_sppf
from .linguify_grammar import linguify_grammar_file

from viper.lexer import Lexeme

from os.path import join, dirname
from typing import List


class Grammar:
    def __init__(self, grammar_filename: str):
        self.file = grammar_filename
        self.rules = linguify_grammar_file(self.file)

    def parse_rule(self, rule: str, lexemes: List[Lexeme]) -> AST:
        lang = self.rules[rule]
        sppf = make_sppf(lang, lexemes)
        if len(sppf) == 0:
            raise RuntimeError("Invalid parse.")
        elif len(sppf) == 1:
            child = sppf[0]
            if not isinstance(child, ParseTreeChar):
                raise RuntimeError(f"Invalid parse result: {child}")
            result = child.token
            if not isinstance(result, AST):
                raise RuntimeError(f"Invalid parse result: {result}")
            return result
        else:
            raise RuntimeError("Ambiguous parse.")


GRAMMAR_FILE = join(dirname(__file__), join('grammar_parsing', 'formal_grammar.bnf'))
GRAMMAR = Grammar(GRAMMAR_FILE)
