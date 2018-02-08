import viper.lexer as vl

from viper.grammar.languages import *

from typing import ClassVar, Dict, List, NamedTuple

ASSIGN_TOKEN = '::='
START_RULE_TOKEN = '<'
END_RULE_TOKEN = '>'

DequotedSubalternate = NamedTuple('DequotedSubalternate', [('text', str), ('is_quoted', bool)])
Alternate = List[DequotedSubalternate]
RawRule = NamedTuple('RawRule', [('name', str), ('raw_alternates', str)])


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

SPECIAL_TOKENS = {
    'INDENT':       INDENT,
    'DEDENT':       DEDENT,
    'NEWLINE':      NEWLINE,
    'PERIOD':       PERIOD,
    '.':            PERIOD,
    'COMMA':        COMMA,
    ',':            COMMA,
    'OPEN_PAREN':   OPEN_PAREN,
    '(':            OPEN_PAREN,
    'CLOSE_PAREN':  CLOSE_PAREN,
    ')':            CLOSE_PAREN,
    'COLON':        COLON,
    ':':            COLON,
    'ARROW':        ARROW,
    '->':           ARROW,
    'NUMBER':       NUMBER,
    'NAME':         NAME,
    'CLASS':        CLASS,
    'OPERATOR':     OPERATOR,
}


def parse_grammar_file(filename: str):
    raw_rules = get_raw_rules_from_file(filename)
    unprocessed_rules = split_alternates(raw_rules)
    quoted_rules = process_alternate_quotes(unprocessed_rules)
    rules = build_language_from_rules(quoted_rules)
    return rules


def get_raw_rules_from_file(filename: str) -> List[RawRule]:
    lines = get_nonempty_lines_from_file(filename)
    rules = {}
    current_rule = None
    for line in lines:
        if line.find(ASSIGN_TOKEN) > 0:
            # This line names a rule.
            if line.count(ASSIGN_TOKEN) > 1:
                # Can only define one rule per line.
                raise RuntimeError(f"Too many rule assignments in one line.")
            # Process the name of the rule.
            name, raw_rule = line.split(ASSIGN_TOKEN)
            name = name.strip()
            if not (name.startswith(START_RULE_TOKEN) and name.endswith(END_RULE_TOKEN)):
                raise RuntimeError(f"Invalid rule name: '{name}'")
            name = name[1:-1]
            # If the rule has not been named previously, create it.
            if name in rules:
                raise RuntimeError(f"Cannot create multiple rules with the same name: '{name}'")
            rules[name] = [raw_rule.strip()]
            current_rule = name
        else:
            if current_rule is None:
                raise RuntimeError(f"First nonempty line must name a new rule.")
            # We must be continuing a rule.
            rules[current_rule].append(line.strip())
    rule_list: List[RawRule] = []
    for name, raw_rules in rules.items():
        alternates = ' '.join(raw_rules)
        rule = RawRule(name, alternates)
        rule_list.append(rule)
    return rule_list


def get_nonempty_lines_from_file(filename: str) -> List[str]:
    lines = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line:
                lines.append(line)
    return lines


def split_alternates(rules: List[RawRule]) -> Dict[str, List[str]]:
    processed_rules = {}
    for rule in rules:
        # Split the rule into its alternates.
        raw_alternates = rule.raw_alternates
        inside_quotes = False
        quote_type = None
        start_index = -1
        alternates = []
        for i, c in enumerate(raw_alternates):
            if c == '"' or c == '\'':
                if inside_quotes and c == quote_type:
                    # Just finished the quoted portion.
                    inside_quotes = False
                elif not inside_quotes:
                    # Starting a quoted string.
                    quote_type = c
                    inside_quotes = True
            elif c == '|' and not inside_quotes:
                # Add this alternate to the list.
                alternates.append(raw_alternates[start_index+1:i])
                start_index = i
        if inside_quotes:
            raise RuntimeError(f"Missing closing quote ({quote_type}) for rule: '{rule.name}'")
        alternates.append(raw_alternates[start_index+1:len(raw_alternates)])
        processed_rules[rule.name] = alternates
    return processed_rules


def process_alternate_quotes(rules: Dict[str, List[str]]) -> Dict[str, List[Alternate]]:
    new_rules: Dict[str, List[Alternate]] = {}
    for name, alternates in rules.items():
        new_rules[name] = []
        for alternate in alternates:
            alt_parts = split_alternate(alternate.strip())
            new_rules[name].append(alt_parts)
    return new_rules


def split_alternate(alternate: str) -> List[DequotedSubalternate]:
    def make_tup(start: int, end: int, quoted: bool):
        substr = alternate[start + 1:end].strip()
        return DequotedSubalternate(substr, quoted)
    parts: List[DequotedSubalternate] = []
    inside_quotes = False
    quote_type = None
    start_index = -1
    for i, c in enumerate(alternate):
        if c == '"' or c == '\'':
            if inside_quotes and c == quote_type:
                # Just finished a quoted portion.
                inside_quotes = False
                parts.append(make_tup(start_index, i, True))
                start_index = i
            elif not inside_quotes:
                # Just finished an unquoted portion; starting a quoted portion.
                quote_type = c
                inside_quotes = True
                parts.append(make_tup(start_index, i, False))
                start_index = i
    # Add the last portion, if there is one.
    if start_index < len(alternate) - 1:
        parts.append(make_tup(start_index, len(alternate), False))
    return parts


def build_language_from_rules(rules: Dict[str, List[Alternate]]) -> Language:
    lang = empty()
    for name, alt_list in rules.items():
        for alternate in alt_list:
            lang = alt(lang, build_language_from_alternate(alternate))
    return lang


# TODO: Remove this eventually.
'''
Grammar productions

<xyz>           == rule 'xyz'; nothing is processed inside angle brackets
SpecialToken    == special token 'SpecialToken'
CapitalWord     == name of class to create for parsing this alternate (if 'CapitalWord' is not a special token)
'word'          == the literal token 'word' (spans spaces)
abc:xyz         == save a parameter named 'abc' with the value of evaluating 'xyz'
@xyz            == evaluate 'xyz' and save its parameters at this level directly (may remove this)
abc:xyz*        == process 'xyz' >=0 times and save all results to parameter 'abc'
&abc{x1,x2}:xyz == process 'xyz', which may return something with names 'x1' or 'x2';
                   accumulate these into a single list 'abc'

All alternates must start with either a CapitalWord or a <rule>.


import sys
sys.path.insert(0, '/Users/pdarragh/Development/Viper/')
from viper.grammar.grammar_parser import *
raw_rules = get_raw_rules_from_file('./viper/grammar/new_formal_grammar.bnf')
unprocessed_rules = split_alternates(raw_rules)
quoted_rules = process_alternate_quotes(unprocessed_rules)
tokens = tokenize_alternate(quoted_rules['trailer'][0])
print(' '.join(map(lambda s: s.text, tokens)))

'''


class AltToken:
    def __init__(self, text: str):
        self.text = text

    def __repr__(self):
        return self.text

    def __str__(self):
        return repr(self)


class LiteralToken(AltToken):
    pass


class RepeatToken(AltToken):
    pass


class OptionalToken(AltToken):
    pass


class ParameterExpansionToken(AltToken):
    pass


class SpecialParameterExpansionToken(AltToken):
    pass


class ColonToken(AltToken):
    pass


class BracedToken(AltToken):
    pass


class RuleToken(AltToken):
    pass


class CapitalWordToken(AltToken):
    pass


class SpecialToken(AltToken):
    pass


class ParameterNameToken(AltToken):
    pass


def parse_token(token: DequotedSubalternate) -> AltToken:
    text = token.text
    if token.is_quoted:
        return LiteralToken(text)
    elif text == '*':
        return RepeatToken(text)
    elif text == '?':
        return OptionalToken(text)
    elif text == '@':
        return ParameterExpansionToken(text)
    elif text == '&':
        return SpecialParameterExpansionToken(text)
    elif text == ':':
        return ColonToken(text)
    elif text.startswith('{') and text.endswith('}'):
        return BracedToken(text[1:-1])
    elif text.startswith('<') and text.endswith('>'):
        return RuleToken(text[1:-1])
    elif text[0].isupper():
        if text in SPECIAL_TOKENS:
            return SpecialToken(text)
        else:
            return CapitalWordToken(text)
    elif text.islower():
        return ParameterNameToken(text)
    else:
        raise ValueError(f"Invalid token: '{text}'")


def parameter_expansion_token(tokens: List[AltToken], index: int):
    # TODO: lookahead for the necessary types of tokens.
    ...


def build_language_from_alternate(alternate: Alternate) -> Language:
    alt_lang = empty()
    tokens = tokenize_alternate(alternate)
    # The first token can either be a CapitalWord or a Rule.
    if isinstance(tokens[0], RuleToken):
        # No other tokens may be present.
        if len(tokens) > 1:
            raise RuntimeError("Alias alternates may not have additional parameters.")
        # TODO: Make new version of Grammar._make_rule for this
        return empty()
    elif isinstance(tokens[0], CapitalWordToken):
        # This alternate must now be parsed.
        i = 1
        while i < len(tokens):
            token = tokens[i]
            # TODO: Attempt parse based on current token (limited possibilities).
            ...
    else:
        # No other tokens can be first.
        raise RuntimeError("Rule alternates must start with either a Rule or a CapitalWord.")


def tokenize_alternate(alternate: Alternate) -> List[AltToken]:
    tokens: List[AltToken] = []
    for subalt in alternate:
        for token in tokenize_subalternate(subalt):
            tokens.append(parse_token(token))
    return tokens


def tokenize_subalternate(subalt: DequotedSubalternate) -> List[DequotedSubalternate]:
    if subalt.is_quoted:
        return [subalt]
    text = subalt.text
    # Create list of tokens.
    subalts: List[DequotedSubalternate] = []
    def add_token(start: int, end: int):
        token = text[start+1:end]
        if token.strip():
            subalts.append(DequotedSubalternate(token, False))
    start_index = -1
    continue_until = None
    i = 0
    while i < len(text):
        c = text[i]
        if continue_until is not None and c != continue_until:
            i += 1
            continue
        if c == ' ' or c == '\t':
            # Whitespace creates tokens automatically.
            add_token(start_index, i)
            start_index = i
        elif c == '<':
            # Rule brackets prevent other tokens from being created.
            add_token(start_index, i)
            start_index = i - 1
            continue_until = '>'
        elif c == '>':
            # Finish the rule bracket.
            add_token(start_index, i + 1)
            start_index = i
            continue_until = None
        elif c == '{':
            # Special braces.
            add_token(start_index, i)
            start_index = i - 1
            continue_until = '}'
        elif c == '}':
            # Finish special braces.
            add_token(start_index, i + 1)
            start_index = i
            continue_until = None
        elif c in ('@', '&', '*', '?', ':'):
            # These characters can only exist independently.
            add_token(start_index, i)
            add_token(i - 1, i + 1)
            start_index = i
        i += 1
    add_token(start_index, i)
    return subalts
