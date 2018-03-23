from .production import *
from .production_part import *
from .tokenize.alt_token import *
from .tokenize.grammar_tokenizer import tokenize_grammar_file

from typing import Dict, List, NamedTuple


TokenParse = NamedTuple('TokenParse', [('part', ProductionPart), ('offset', int)])


def parse_grammar_file(filename: str) -> Dict[str, List[ProductionPart]]:
    tokenized_rules = tokenize_grammar_file(filename)
    parsed_rules = {}
    for name, rule in tokenized_rules.items():
        parsed_rule = parse_rule(rule)
        parsed_rules[name] = parsed_rule
    return parsed_rules


def parse_rule(rule: List[List[AltToken]]) -> List[ProductionPart]:
    parsed_alternates = []
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
    Match           = '@'? MatchOpt
    MatchOpt        = Literal
                    | DynamicMatch
    DynamicMatch    = SpecialMatch
                    | RuleMatch
    SpecialMatch    = Special ('*' | '?')?
    RuleMatch       = Rule ('*' | '?')?
    Save            = ParamSpec ':' DynamicMatch
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
            parse = parse_literal_token(token_list, i)
        elif isinstance(token, SpecialToken):
            parse = parse_special_token(token_list, i)
        elif isinstance(token, ParameterNameToken):
            parse = parse_parameter_name_token(token_list, i)
        elif isinstance(token, ParameterExpansionToken):
            parse = parse_parameter_expansion_token(token_list, i)
        elif isinstance(token, SpecialParameterExpansionToken):
            parse = parse_special_parameter_expansion_token(token_list, i)
        else:
            # TODO: Make custom error here.
            raise RuntimeError
        parts.append(parse.part)
        i += parse.offset
    return NamedProduction(name, parts)


def parse_literal_token(token_list: List[AltToken], index: int) -> TokenParse:
    part = LiteralPart(token_list[index].text)
    return TokenParse(part, 1)


def parse_special_token(token_list: List[AltToken], index: int) -> TokenParse:
    return parse_special_token_or_rule_token(token_list, index, True)


def parse_parameter_name_token(token_list: List[AltToken], index: int) -> TokenParse:
    pass


def parse_parameter_expansion_token(token_list: List[AltToken], index: int) -> TokenParse:
    pass


def parse_special_parameter_expansion_token(token_list: List[AltToken], index: int) -> TokenParse:
    pass


def parse_special_token_or_rule_token(token_list: List[AltToken], index: int, is_special: bool) -> TokenParse:
    pass
