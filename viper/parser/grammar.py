from viper.parser.languages import *

import viper.lexer as vl

from os.path import dirname, join
from typing import ClassVar, List

__all__ = ['GRAMMAR']


class GrammarToken:
    def __init__(self, lexeme_class: ClassVar):
        self._lexeme_class = lexeme_class

    def __eq__(self, other):
        if isinstance(other, GrammarToken):
            return self._lexeme_class == other._lexeme_class
        elif isinstance(other, Literal):
            return other.lit == self
        return isinstance(other, self._lexeme_class)

    def __str__(self):
        return f'{self._lexeme_class.__name__}Token'

    def __repr__(self):
        return str(self)


class GrammarLiteral:
    def __init__(self, val: str):
        self._val = val

    def __eq__(self, other):
        if isinstance(other, GrammarLiteral):
            return self._val == other._val
        if isinstance(other, vl.Lexeme):
            return self._val == other.text
        return False

    def __str__(self):
        return f'"{self._val}"'

    def __repr__(self):
        return str(self)


class RuleLiteral(Language):
    def __init__(self, rule: str, grammar):
        self.rule = rule
        self.grammar = grammar

    def __eq__(self, other):
        if isinstance(other, RuleLiteral):
            return self.rule == other.rule
        if isinstance(other, Language):
            return self.grammar[self.rule] == other
        return False

    def __str__(self):
        return f'<{self.rule}>'

    def __nullable__(self) -> bool:
        return nullable(self.grammar[self.rule])

    def __derive__(self, c):
        return derive(self.grammar[self.rule], c)


INDENT = GrammarToken(vl.Indent)
DEDENT = GrammarToken(vl.Dedent)
NEWLINE = GrammarToken(vl.NewLine)
PERIOD = GrammarToken(vl.Period)
COMMA = GrammarToken(vl.Comma)
OPEN_PAREN = GrammarToken(vl.OpenParen)
CLOSE_PAREN = GrammarToken(vl.CloseParen)
COLON = GrammarToken(vl.Colon)
ARROW = GrammarToken(vl.Arrow)
NUMBER = GrammarToken(vl.Number)
NAME = GrammarToken(vl.Name)
CLASS = GrammarToken(vl.Class)
OPERATOR = GrammarToken(vl.Operator)


class GrammarParseError(Exception):
    def __init__(self, message='', line_no=None):
        if line_no is not None:
            message = f'[{line_no}]: {message}'
        super().__init__(message)


class ParseError(ValueError):
    pass


class Grammar:
    def __init__(self, grammar_file: str):
        self._grammar_dict = {}
        self._parse_file(grammar_file)
        self.grammar = Union(*self._grammar_dict.values())

    def partial_parse(self, lexemes: List[vl.Lexeme]):
        lang = self.grammar
        for lexeme in lexemes:
            lang = derive(lang, lexeme)
        return lang

    def _parse_file(self, grammar_file: str):
        raw_rules = {}
        with open(grammar_file) as gf:
            line_no = 0
            for line in gf:
                line = line.strip()
                line_no += 1
                if not line:
                    continue
                if line.startswith('#'):
                    continue
                try:
                    name, raw_rule = self._split_line(line)
                except Exception as e:
                    if len(e.args) > 0:
                        msg = e.args[0]
                    else:
                        msg = ''
                    raise GrammarParseError(msg, line_no)
                raw_rules[name] = raw_rule
        self._parse_rules(raw_rules)

    @staticmethod
    def _split_line(line: str):
        name, rule = line.split('::=')
        name = name.strip()
        if not (name.startswith('<') and name.endswith('>')):
            raise ValueError(f"no angle brackets around production name: {name}")
        name = name[1:-1]
        rule = rule.strip()
        return name, rule

    def _parse_rules(self, raw_rules):
        for name, raw_rule_list in raw_rules.items():
            rule_tup = (self._parse_rule(raw_rule) for raw_rule in raw_rule_list.split('|'))
            self._grammar_dict[name] = Union(*rule_tup)

    def _parse_rule(self, rule: str) -> Language:
        raw_tokens = rule.split()
        rule_parts = []
        for raw_token in raw_tokens:
            token = self._parse_token(raw_token)
            rule_parts.append(token)
        rule = Concat(*rule_parts)
        return rule

    def _parse_token(self, token: str) -> Language:
        if token == 'INDENT':
            return Literal(INDENT)
        if token == 'DEDENT':
            return Literal(DEDENT)
        if token == 'NEWLINE':
            return Literal(NEWLINE)
        if token == 'PERIOD' or token == '.':
            return Literal(PERIOD)
        if token == 'COMMA' or token == ',':
            return Literal(COMMA)
        if token == 'OPEN_PAREN' or token == '(':
            return Literal(OPEN_PAREN)
        if token == 'CLOSE_PAREN' or token == ')':
            return Literal(CLOSE_PAREN)
        if token == 'COLON' or token == ':':
            return Literal(COLON)
        if token == 'ARROW' or token == '->':
            return Literal(ARROW)
        if token == 'NAME':
            return Literal(NAME)
        if token == 'CLASS':
            return Literal(CLASS)
        if token == 'OPERATOR':
            return Literal(OPERATOR)
        if token.startswith('<') and token.endswith('>'):
            return self._make_rule(token[1:-1])
        if token.endswith('?'):
            subtoken = self._parse_token(token[:-1])
            if isinstance(subtoken, RuleLiteral):
                return Optional(subtoken)
            else:
                raise GrammarParseError(f"optional wrapping non-rule production: {subtoken}")
        if token.endswith('*'):
            subtoken = self._parse_token(token[:-1])
            if isinstance(subtoken, RuleLiteral):
                return Repeat(subtoken)
            else:
                raise GrammarParseError(f"repeat-star wrapping non-rule production: {subtoken}")
        return Literal(GrammarLiteral(token))

    def _make_rule(self, rule):
        return RuleLiteral(rule, self._grammar_dict)


GRAMMAR_FILE = join(dirname(__file__), 'formal_grammar.bnf')
GRAMMAR = Grammar(GRAMMAR_FILE)
