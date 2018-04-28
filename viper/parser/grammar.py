from .ast.nodes import AST
from .languages import ParseTreeChar, make_sppf, SPPF
from .linguify_grammar import linguify_grammar_file

from viper.lexer import Lexeme

from os.path import join, dirname
from typing import List


class Parse:
    pass


class NoParse(Parse):
    pass


class SingleParse(Parse):
    def __init__(self, parse: AST):
        self.ast = parse


class MultipleParse(Parse):
    def __init__(self, parses: List[AST]):
        self.asts = parses


class Grammar:
    def __init__(self, grammar_filename: str):
        self.file = grammar_filename
        self.rules = linguify_grammar_file(self.file)

    def sppf_from_rule(self, rule: str, lexemes: List[Lexeme]) -> SPPF:
        lang = self.rules[rule]
        return make_sppf(lang, lexemes)

    def parse_rule(self, rule: str, lexemes: List[Lexeme]) -> Parse:
        sppf = self.sppf_from_rule(rule, lexemes)
        parses = []
        for child in sppf:
            if not isinstance(child, ParseTreeChar):
                raise RuntimeError(f"Invalid parse result: {child}")
            result = child.token
            if not isinstance(result, AST):
                raise RuntimeError(f"Invalid parse result: {result}")
            parses.append(result)
        if len(parses) == 0:
            return NoParse()
        elif len(parses) == 1:
            return SingleParse(parses[0])
        else:
            return MultipleParse(parses)

    def parse_file(self, lexemes: List[Lexeme]) -> Parse:
        return self.parse_rule('file_input', lexemes)


GRAMMAR_FILE = join(dirname(__file__), join('grammar_parsing', 'formal_grammar.bnf'))
GRAMMAR = Grammar(GRAMMAR_FILE)
