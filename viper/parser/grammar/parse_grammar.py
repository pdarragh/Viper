from .production import *
from .production_part import *
from .tokenize.alt_token import *
from .tokenize.grammar_tokenizer import tokenize_grammar_file

from typing import Dict, List, NamedTuple

TokenParse = NamedTuple('TokenParse', [('part', ProductionPart), ('idx', int)])


def parse_grammar_file(filename: str) -> Dict[str, List[Production]]:
    tokenized_rules = tokenize_grammar_file(filename)
    parsed_rules = {}
    for name, rule in tokenized_rules.items():
        parsed_rule = parse_rule(rule)
        parsed_rules[name] = parsed_rule
    return parsed_rules


def parse_rule(rule: List[List[AltToken]]) -> List[Production]:
    parsed_alternates: List[Production] = []
    for alternate in rule:
        parsed_alternate = parse_alternate(alternate)
        parsed_alternates.append(parsed_alternate)
    return parsed_alternates


def parse_alternate(token_list: List[AltToken]) -> Production:
    head = token_list[0]
    if isinstance(head, RuleToken):
        if len(token_list) > 1:
            # TODO: Make custom error here.
            raise RuntimeError
        return parse_rule_alias(head)
    elif isinstance(head, CapitalWordToken):
        return parse_production(token_list)
    else:
        # TODO: Make custom error here.
        raise RuntimeError


def parse_rule_alias(token: RuleToken) -> RuleAliasProduction:
    rule_name = token.text
    return RuleAliasProduction(rule_name)


def parse_production(token_list: List[AltToken]) -> NamedProduction:
    """
    Grammar productions follow their own (very simple) grammar:

    Prod            = RuleAlias
                    | ProdName (Match | Save)+
    RuleAlias       = Rule
    Match           = MatchOpt
                    | '@' Rule
    MatchOpt        = Literal
                    | StaticMatch
    StaticMatch     = SpecialMatch
                    | RuleMatch
    SpecialMatch    = Special ('*' | '?')?
    RuleMatch       = Rule ('*' | '?')?
    Save            = ParamSpec ':' StaticMatch
    ParamSpec       = ParamName
                    | '&' ParamName '{' ParamName ',' ParamName '}'
    ParamName       = LITERAL
    Literal         = "'" LITERAL "'"
    Special         = SPECIAL
    Rule            = '<' LITERAL '>'

    :param token_list:
    :return:
    """
    parts: List[ProductionPart] = []
    name = token_list[0].text
    i = 1
    while i < len(token_list):
        token = token_list[i]
        if isinstance(token, LiteralToken):
            parse = parse_literal(token_list, i)
        elif isinstance(token, SpecialToken):
            parse = parse_special_literal(token_list, i)
        elif isinstance(token, ParameterNameToken):
            parse = parse_regular_parameter(token_list, i)
        elif isinstance(token, ParameterExpansionToken):
            parse = parse_expanded_parameter(token_list, i)
        elif isinstance(token, SpecialParameterExpansionToken):
            parse = parse_special_expanded_parameter(token_list, i)
        else:
            # TODO: Make custom error here.
            raise RuntimeError
        parts.append(parse.part)
        i = parse.idx
    return NamedProduction(name, parts)


def parse_literal(token_list: List[AltToken], index: int) -> TokenParse:
    return TokenParse(LiteralPart(token_list[index].text), index + 1)


def parse_special_literal(token_list: List[AltToken], index: int) -> TokenParse:
    return TokenParse(SpecialPart(token_list[index].text), index + 1)


def parse_rule_literal(token_list: List[AltToken], index: int) -> TokenParse:
    token = token_list[index]
    if not isinstance(token, RuleToken):
        # TODO: Make custom error here.
        raise RuntimeError
    return TokenParse(RulePart(token_list[index].text), index + 1)


def parse_regular_parameter(token_list: List[AltToken], index: int) -> TokenParse:
    parameter_name = token_list[index].text
    if not isinstance(token_list[index + 1], ColonToken):
        # TODO: Make custom error here.
        raise RuntimeError
    index += 2
    match_token = token_list[index]
    if isinstance(match_token, SpecialToken):
        match_parse = parse_special_literal(token_list, index)
    elif isinstance(match_token, RuleToken):
        match_parse = parse_rule_literal(token_list, index)
    else:
        # TODO: Make custom error here.
        raise RuntimeError
    match_parse = parse_possible_repeatable_or_optional(token_list, match_parse.idx, match_parse.part)
    return TokenParse(ParameterPart(parameter_name, match_parse.part), match_parse.idx)


def parse_expanded_parameter(token_list: List[AltToken], index: int) -> TokenParse:
    rule_parse = parse_rule_literal(token_list, index + 1)
    return TokenParse(ExpandedParameterPart(rule_parse.part), rule_parse.idx)


def parse_special_expanded_parameter(token_list: List[AltToken], index: int) -> TokenParse:
    name_token = token_list[index + 1]
    if not isinstance(name_token, ParameterNameToken):
        # TODO: Make custom error here.
        raise RuntimeError
    parameter_name = name_token.text
    brace_token = token_list[index + 2]
    if not isinstance(brace_token, BracedToken):
        # TODO: Make custom error here.
        raise RuntimeError
    if not isinstance(token_list[index + 3], ColonToken):
        # TODO: Make custom error here.
        raise RuntimeError
    rule_parse = parse_rule_literal(token_list, index + 4)
    part = SpecialExpandedParameterPart(parameter_name, brace_token.left, brace_token.right, rule_parse.part)
    return parse_possible_optional(token_list, rule_parse.idx, part)


def parse_possible_repeatable_or_optional(token_list: List[AltToken],
                                          index: int,
                                          enclosed_part: ProductionPart) -> TokenParse:
    if index >= len(token_list):
        return TokenParse(enclosed_part, index)
    token = token_list[index]
    if isinstance(token, RepeatToken):
        return TokenParse(RepeatPart(enclosed_part), index + 1)
    else:
        return parse_possible_optional(token_list, index, enclosed_part)


def parse_possible_optional(token_list: List[AltToken], index: int, enclosed_part: ProductionPart) -> TokenParse:
    if index >= len(token_list) or not isinstance(token_list[index], OptionalToken):
        return TokenParse(enclosed_part, index)
    else:
        return TokenParse(OptionPart(enclosed_part), index + 1)
