import viper.parser.languages as vpl

from typing import Dict

RulesDict = Dict[str, vpl.Language]
RawRulesDict = Dict[str, str]


class Token:
    def __str__(self):
        return 'Token'

    def __repr__(self):
        return str(self)


class Rule(Token):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f'<{self.name}>'


class Repeat(Token):
    def __init__(self, token: Token):
        self.token = token

    def __str__(self):
        return f'{self.token}*'


class Optional(Token):
    def __init__(self, token: Token):
        self.token = token

    def __str__(self):
        return f'{self.token}?'


class Class(Token):
    def __str__(self):
        return 'CLASS'


class Name(Token):
    def __str__(self):
        return 'NAME'


class Literal(Token):
    def __init__(self, lit: str):
        self.lit = lit

    def __str__(self):
        return f'\'{self.lit}\''


class GrammarParserError(Exception):
    def __init__(self, message='', line_no=None):
        if line_no is not None:
            message = f'[{line_no}]: {message}'
        super().__init__(message)


class GrammarParser:
    def __init__(self, grammar_file: str):
        self.rules: RulesDict = {}
        self._parse_file(grammar_file)

    def _parse_file(self, grammar_file: str):
        raw_rules: RawRulesDict = {}
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
                    raise GrammarParserError(msg, line_no)
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

    def _parse_rules(self, raw_rules: RawRulesDict):
        for name, raw_rule_list in raw_rules.items():
            rule_tup = (self._parse_raw_rule(raw_rule) for raw_rule in raw_rule_list.split('|'))
            self.rules[name] = vpl.Union(*rule_tup)

    def _parse_raw_rule(self, raw_rule: str) -> vpl.Language:
        raw_tokens = raw_rule.split()
        rule_parts = []
        for raw_token in raw_tokens:
            token = self._parse_token(raw_token)
            if isinstance(token, Repeat):
                rule_parts.append(vpl.Repeat(vpl.Literal(token.token)))
            elif isinstance(token, Optional):
                rule_parts.append(vpl.Union(vpl.Literal(token.token), vpl.EPSILON))
            else:
                rule_parts.append(vpl.Literal(token))
        rule = vpl.Concat(*rule_parts)
        return rule

    def _parse_token(self, token: str) -> Token:
        if token == 'CLASS':
            return Class()
        if token == 'NAME':
            return Name()
        if token.startswith('<') and token.endswith('>'):
            return Rule(token[1:-1])
        if token.endswith('?'):
            subtoken = self._parse_token(token[:-1])
            if isinstance(subtoken, Rule):
                return Optional(subtoken)
            else:
                raise GrammarParserError(f"optional wrapping non-rule production: {subtoken}")
        if token.endswith('*'):
            subtoken = self._parse_token(token[:-1])
            if isinstance(subtoken, Rule):
                return Optional(subtoken)
            else:
                raise GrammarParserError(f"repeat star wrapping non-rule production: {subtoken}")
        return Literal(token)
