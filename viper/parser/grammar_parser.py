import viper.lexer as vl

from viper.parser.languages import *

from os.path import dirname, join as join_paths
from typing import ClassVar, Dict, List, NamedTuple, Tuple, Type

# TODO: use a single AST class and pass alternate names along as an argument

ASSIGN_TOKEN = '::='
START_RULE_TOKEN = '<'
END_RULE_TOKEN = '>'

DequotedSubalternate = NamedTuple('DequotedSubalternate', [('text', str), ('is_quoted', bool)])
Alternate = List[DequotedSubalternate]
RawRule = NamedTuple('RawRule', [('name', str), ('raw_alternates', str)])
TokenParse = NamedTuple('TokenParse', [('lang', Language), ('offset', int)])


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
ENDMARKER = GrammarToken(vl.EndMarker)
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
    'ENDMARKER':    ENDMARKER,
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


class AltToken:
    def __init__(self, text: str):
        self.text = text

    def __repr__(self):
        return self.text

    def __str__(self):
        return repr(self)


class LiteralToken(AltToken):
    def __repr__(self):
        return '\'' + self.text + '\''


class SpecialToken(AltToken):
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
    def __repr__(self):
        return '{' + self.text + '}'


class RuleToken(AltToken):
    def __repr__(self):
        return '<' + self.text + '>'


class CapitalWordToken(AltToken):
    pass


class ParameterNameToken(AltToken):
    pass


class GrammarFileParseError(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class Grammar:
    def __init__(self, grammar_filename: str):
        self._grammar_dict = {}
        self._rule_line_nos = {}
        self._parse_grammar_file(grammar_filename)
        self.grammar = alt(*self._grammar_dict.values())

    def partial_parse(self, lexemes: List[vl.Lexeme], lang=None) -> SPPF:
        if lang is None:
            lang = self.grammar
        return make_sppf(lang, lexemes)

    def get_rule(self, rule: str) -> Language:
        return self._grammar_dict.get(rule, empty())

    def parse_rule(self, rule: str, lexemes: List[vl.Lexeme]) -> SPPF:
        lang = self.get_rule(rule)
        return self.partial_parse(lexemes, lang)

    def parse_single(self, lexemes: List[vl.Lexeme]) -> SPPF:
        return self.parse_rule('single_input', lexemes)

    def parse_file(self, lexemes: List[vl.Lexeme]) -> SPPF:
        return self.parse_rule('file_input', lexemes)

    def _parse_grammar_file(self, filename: str):
        raw_rules, line_nos = get_raw_rules_from_file(filename)
        self._rule_line_nos = line_nos
        split_rules = split_alternates(raw_rules)
        dequoted_rules = process_alternate_quotes(split_rules)
        self.process_dequoted_rules(dequoted_rules)

    def process_dequoted_rules(self, rules: Dict[str, List[Alternate]]):
        for name, alt_list in rules.items():
            rule_lang_parts = []
            try:
                for alternate in alt_list:
                    alternate_lang = self.process_alternate(alternate)
                    rule_lang_parts.append(alternate_lang)
            except GrammarFileParseError as e:
                # Inject the rule name and that rule's initial line number into the message.
                msg = f"Error parsing rule <{name}> on line {self._rule_line_nos[name]}: {e.msg}"
                err = GrammarFileParseError(msg)
                err.__traceback__ = e.__traceback__
                raise err
            self._grammar_dict[name] = alt(*rule_lang_parts)

    def process_alternate(self, alternate: Alternate) -> Language:
        alternate_lang_parts = []
        tokens = tokenize_alternate(alternate)
        # The first token can either be a CapitalWord or a Rule.
        if isinstance(tokens[0], RuleToken):
            # No other tokens may be present.
            if len(tokens) > 1:
                raise GrammarFileParseError("Alias alternates may not have additional parameters.")
            return self._make_rule_literal(tokens[0].text)
        elif isinstance(tokens[0], CapitalWordToken):
            alternate_name = tokens[0].text
            args = {}
            i = 1
            while i < len(tokens):
                token = tokens[i]
                if isinstance(token, LiteralToken):
                    parse = self._parse_literal_token(tokens, i)
                elif isinstance(token, SpecialToken):
                    parse = self._parse_special_token(tokens, i)
                elif isinstance(token, ParameterExpansionToken):
                    parse = self._parse_parameter_expansion_token(tokens, i)
                elif isinstance(token, SpecialParameterExpansionToken):
                    parse = self._parse_special_parameter_expansion_token(tokens, i)
                elif isinstance(token, ParameterNameToken):
                    parse = self._parse_parameter_name_token(tokens, i)
                else:
                    raise GrammarFileParseError(f"Cannot process rule part beginning with token: '{token}'")
                alternate_lang_parts.append(parse.lang)
                i += parse.offset
            return concat(*alternate_lang_parts)
        else:
            # No other tokens can be first.
            raise GrammarFileParseError("Rule alternates must start with either a Rule or a CapitalWord.")

    @staticmethod
    def _verify_token_sequence(tokens: List[AltToken], index: int, match: List[Type[AltToken]]):
        for offset, class_var in enumerate(match):
            token = tokens[index + offset]
            if not isinstance(token, class_var):
                given_type = type(token).__name__
                expected_type = class_var.__name__
                raise GrammarFileParseError(f"Token '{token}' does not match expected type.\n"
                                            f"    Given type:    {given_type}\n"
                                            f"    Expected type: {expected_type}")

    @staticmethod
    def _parse_literal_token(tokens: List[AltToken], index: int) -> TokenParse:
        lang = literal(GrammarLiteral(tokens[index].text))
        return TokenParse(lang, 1)

    def _parse_parameter_expansion_token(self, tokens: List[AltToken], index: int) -> TokenParse:
        seq = [ParameterExpansionToken, RuleToken]
        self._verify_token_sequence(tokens, index, seq)
        rule = tokens[index + 1]
        lang = self._make_rule_literal(rule.text)
        return TokenParse(lang, 2)

    @staticmethod
    def _split_braced_token(token: AltToken) -> Tuple[str, str]:
        if not isinstance(token, BracedToken):
            raise GrammarFileParseError(f"Cannot split non-braced token: '{token}'")
        text = token.text
        left, right = text.split(',')
        return left.strip(), right.strip()

    def _parse_special_parameter_expansion_token(self, tokens: List[AltToken], index: int) -> TokenParse:
        seq = [SpecialParameterExpansionToken, ParameterNameToken, BracedToken, ColonToken, RuleToken]
        self._verify_token_sequence(tokens, index, seq)
        name = tokens[index + 1]
        braced = tokens[index + 2]
        singular, plural = self._split_braced_token(braced)
        intmd_result = self._parse_rule_token(tokens, index + 4)
        return TokenParse(intmd_result.lang, 4 + intmd_result.offset)

    def _parse_rule_or_special_token(self, tokens: List[AltToken], index: int, is_rule: bool) -> TokenParse:
        # Prepare the bare language.
        if is_rule:
            lang = self._make_rule_literal(tokens[index].text)
        else:
            lang = Literal(SPECIAL_TOKENS[tokens[index].text])
        # Lookahead to the token after the rule.
        succ = None
        if index + 1 < len(tokens):
            succ = tokens[index + 1]
        if isinstance(succ, RepeatToken):
            return TokenParse(rep(lang), 2)
        elif isinstance(succ, OptionalToken):
            return TokenParse(opt(lang), 2)
        else:
            return TokenParse(lang, 1)

    def _parse_rule_token(self, tokens: List[AltToken], index: int) -> TokenParse:
        return self._parse_rule_or_special_token(tokens, index, True)

    def _parse_special_token(self, tokens: List[AltToken], index: int) -> TokenParse:
        return self._parse_rule_or_special_token(tokens, index, False)

    def _parse_parameter_name_token(self, tokens: List[AltToken], index: int) -> TokenParse:
        if isinstance(tokens[index + 2], RuleToken):
            return self._parse_parameter_name_rule_token(tokens, index)
        elif isinstance(tokens[index + 2], SpecialToken):
            return self._parse_parameter_name_special_token(tokens, index)
        else:
            raise GrammarFileParseError(f"Invalid token given as argument to named parameter: {tokens[index + 2]}")

    def _parse_parameter_name_rule_token(self, tokens: List[AltToken], index: int) -> TokenParse:
        seq = [ParameterNameToken, ColonToken, RuleToken]
        self._verify_token_sequence(tokens, index, seq)
        name = tokens[index]
        intmd_result = self._parse_rule_token(tokens, index + 2)
        return TokenParse(intmd_result.lang, 2 + intmd_result.offset)

    def _parse_parameter_name_special_token(self, tokens: List[AltToken], index: int) -> TokenParse:
        seq = [ParameterNameToken, ColonToken, SpecialToken]
        self._verify_token_sequence(tokens, index, seq)
        name = tokens[index]
        intmd_result = self._parse_special_token(tokens, index + 2)
        return TokenParse(intmd_result.lang, 2 + intmd_result.offset)

    def _make_rule_literal(self, rule_name: str):
        return RuleLiteral(rule_name, self._grammar_dict)


"""
import sys
sys.path.insert(0, '/Users/pdarragh/Development/Viper')
from viper.parser import GRAMMAR as G
from viper.parser.languages import *
from viper.lexer import lex_line, lex_lines, lex_file

"""


def get_raw_rules_from_file(filename: str) -> Tuple[List[RawRule], Dict[str, int]]:
    rules = {}
    line_nos = {}
    current_rule = None
    i = 0
    with open(filename) as f:
        for line in f:
            i += 1
            line = line.strip()
            if line.startswith('#') or not line:
                continue
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
                line_nos[name] = i
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
    return rule_list, line_nos


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
from viper.parser.grammar_parser import *
raw_rules = get_raw_rules_from_file('./viper/parser/formal_grammar.bnf')
unprocessed_rules = split_alternates(raw_rules)
quoted_rules = process_alternate_quotes(unprocessed_rules)
tokens = tokenize_alternate(quoted_rules['trailer'][0])
print(' '.join(map(lambda s: s.text, tokens)))

'''


def tokenize_dequoted_subalternate(token: DequotedSubalternate) -> AltToken:
    text = token.text
    if token.is_quoted:
        if text in SPECIAL_TOKENS:
            return SpecialToken(text)
        else:
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


def tokenize_alternate(alternate: Alternate) -> List[AltToken]:
    tokens: List[AltToken] = []
    for subalt in alternate:
        for token in tokenize_subalternate(subalt):
            tokens.append(tokenize_dequoted_subalternate(token))
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


GRAMMAR_FILE = join_paths(dirname(__file__), join_paths('grammar', 'formal_grammar.bnf'))
GRAMMAR = Grammar(GRAMMAR_FILE)


if __name__ == '__main__':
    from viper.lexer import lex_line
    tokens = lex_line('()')
    sppf = make_sppf(GRAMMAR.get_rule('atom'), tokens)
    print(sppf)
