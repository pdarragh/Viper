import viper.lexer as vl

from viper.grammar.languages import *

from os.path import dirname, join
from typing import ClassVar, List


class GrammarToken:
    def __init__(self, lexeme_class: ClassVar, text=None):
        self._lexeme_class = lexeme_class
        self._text = text

    def __eq__(self, other):
        if isinstance(other, GrammarToken):
            return self._lexeme_class == other._lexeme_class
        elif isinstance(other, Literal):
            return other.value == self
        return isinstance(other, self._lexeme_class)

    def __str__(self):
        if self._text is not None:
            return self._text
        else:
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


INDENT = GrammarToken(vl.Indent)
DEDENT = GrammarToken(vl.Dedent)
NEWLINE = GrammarToken(vl.NewLine)
PERIOD = GrammarToken(vl.Period, vl.PERIOD.text)
COMMA = GrammarToken(vl.Comma, vl.COMMA.text)
OPEN_PAREN = GrammarToken(vl.OpenParen, vl.OPEN_PAREN.text)
CLOSE_PAREN = GrammarToken(vl.CloseParen, vl.CLOSE_PAREN.text)
COLON = GrammarToken(vl.Colon, vl.COLON.text)
ARROW = GrammarToken(vl.Arrow, vl.ARROW.text)
NUMBER = GrammarToken(vl.Number)
NAME = GrammarToken(vl.Name)
CLASS = GrammarToken(vl.Class)
OPERATOR = GrammarToken(vl.Operator)


class GrammarParseError(Exception):
    def __init__(self, message='', line_no=None):
        if line_no is not None:
            message = f'[{line_no}]: {message}'
        super().__init__(message)


class Grammar:
    def __init__(self, grammar_file: str):
        self._grammar_dict = {}
        self._parse_file(grammar_file)
        self.grammar = alt(*self._grammar_dict.values())

    def partial_parse(self, lexemes: List[vl.Lexeme]):
        lang = self.grammar
        for lexeme in lexemes:
            lang = derive(lang, lexeme)
        return lang

    def parse_single(self, lexemes: List[vl.Lexeme]):
        lang = self._grammar_dict['single_line']
        for lexeme in lexemes:
            lang = derive(lang, lexeme)
        return lang

    def parse_multiple(self, lexemes: List[vl.Lexeme]):
        lang = self._grammar_dict['many_lines']
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
            self._grammar_dict[name] = alt(*rule_tup)

    def _parse_rule(self, rule: str) -> Language:
        raw_tokens = rule.split()
        rule_parts = []
        for raw_token in raw_tokens:
            token = self._parse_token(raw_token)
            rule_parts.append(token)
        rule = concat(*rule_parts)
        return rule

    def _parse_token(self, token: str) -> Language:
        if token == 'INDENT':
            return literal(INDENT)
        if token == 'DEDENT':
            return literal(DEDENT)
        if token == 'NEWLINE':
            return literal(NEWLINE)
        if token == 'PERIOD' or token == '.':
            return literal(PERIOD)
        if token == 'COMMA' or token == ',':
            return literal(COMMA)
        if token == 'OPEN_PAREN' or token == '(':
            return literal(OPEN_PAREN)
        if token == 'CLOSE_PAREN' or token == ')':
            return literal(CLOSE_PAREN)
        if token == 'COLON' or token == ':':
            return literal(COLON)
        if token == 'ARROW' or token == '->':
            return literal(ARROW)
        if token == 'NAME':
            return literal(NAME)
        if token == 'CLASS':
            return literal(CLASS)
        if token == 'OPERATOR':
            return literal(OPERATOR)
        if token.startswith('<') and token.endswith('>'):
            return self._make_rule(token[1:-1])
        if token.endswith('?'):
            subtoken = self._parse_token(token[:-1])
            if isinstance(subtoken, RuleLiteral):
                return opt(subtoken)
            else:
                raise GrammarParseError(f"optional wrapping non-rule production: {subtoken}")
        if token.endswith('*'):
            subtoken = self._parse_token(token[:-1])
            if isinstance(subtoken, RuleLiteral):
                return rep(subtoken)
            else:
                raise GrammarParseError(f"repeat-star wrapping non-rule production: {subtoken}")
        return literal(GrammarLiteral(token))

    def _make_rule(self, rule):
        return RuleLiteral(rule, self._grammar_dict)


GRAMMAR_FILE = join(dirname(__file__), 'formal_grammar.bnf')
GRAMMAR = Grammar(GRAMMAR_FILE)
