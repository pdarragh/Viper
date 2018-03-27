from .alt_token import *
from .special_tokens import SPECIAL_TOKENS

from viper.error import ViperError

from typing import Dict, List, NamedTuple, Tuple


ASSIGN_TOKEN = '::='
START_RULE_TOKEN = '<'
END_RULE_TOKEN = '>'

DequotedSubalternate = NamedTuple('DequotedSubalternate', [('text', str), ('is_quoted', bool)])
Alternate = List[DequotedSubalternate]
RawRule = NamedTuple('RawRule', [('name', str), ('raw_alternates', str)])


class TokenizerError(ViperError):
    pass


def tokenize_grammar_file(filename: str) -> Dict[str, List[List[AltToken]]]:
    raw_rules, line_nos = get_raw_rules_and_line_numbers_from_file(filename)
    split_rules = split_rule_alternates(raw_rules)
    dequoted_rules = process_alternate_quotes(split_rules)
    final_rules = tokenize_dequoted_rules(dequoted_rules)
    return final_rules


def get_raw_rules_and_line_numbers_from_file(filename: str) -> Tuple[List[RawRule], Dict[str, int]]:
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
                    raise TokenizerError(f"Too many rule assignments in one line.")
                # Process the name of the rule.
                name, raw_rule = line.split(ASSIGN_TOKEN)
                name = name.strip()
                if not (name.startswith(START_RULE_TOKEN) and name.endswith(END_RULE_TOKEN)):
                    raise TokenizerError(f"Invalid rule name: '{name}'")
                name = name[1:-1]
                # If the rule has not been named previously, create it.
                if name in rules:
                    raise TokenizerError(f"Cannot create multiple rules with the same name: '{name}'")
                rules[name] = [raw_rule.strip()]
                line_nos[name] = i
                current_rule = name
            else:
                if current_rule is None:
                    raise TokenizerError(f"First nonempty line must name a new rule.")
                # We must be continuing a rule.
                rules[current_rule].append(line.strip())
    rule_list: List[RawRule] = []
    for name, raw_rules in rules.items():
        alternates = ' '.join(raw_rules)
        rule = RawRule(name, alternates)
        rule_list.append(rule)
    return rule_list, line_nos


def split_rule_alternates(raw_rules: List[RawRule]) -> Dict[str, List[str]]:
    processed_rules: Dict[str, List[str]] = {}
    for rule in raw_rules:
        # Split the rule into its alternates.
        raw_alternates = rule.raw_alternates
        inside_quotes = False
        quote_type = None
        start_index = -1
        alternates: List[str] = []
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
            raise TokenizerError(f"Missing closing quote ({quote_type}) for rule: '{rule.name}'")
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


def tokenize_dequoted_rules(dequoted_rules: Dict[str, List[Alternate]]) -> Dict[str, List[List[AltToken]]]:
    tokenized_rules: Dict[str, List[List[AltToken]]] = {}
    for name, alt_list in dequoted_rules.items():
        alternate_token_lists: List[List[AltToken]] = []
        for alternate in alt_list:
            tokens = tokenize_alternate(alternate)
            alternate_token_lists.append(tokens)
        tokenized_rules[name] = alternate_token_lists
    return tokenized_rules


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
        parts = text[1:-1].split(',')
        if len(parts) != 2:
            raise TokenizerError("Invalid braced expression: '{text}'")
        return BracedToken(parts[0].strip(), parts[1].strip())
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
        raise TokenizerError(f"Invalid token: '{text}'")
