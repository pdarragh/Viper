from .grammar.parse_grammar import parse_grammar_file
from .grammar.production import *
from .languages import *

from viper.error import ViperError

from typing import Dict, List


RuleDict = Dict[str, Language]


class LinguifierError(ViperError):
    pass


def linguify_grammar_file(filename: str) -> RuleDict:
    parsed_rules = parse_grammar_file(filename)
    rule_langs = []
    rule_dict = {}
    for rule, production_list in parsed_rules.items():
        lang = linguify_rule(production_list, rule_dict)
        rule_langs.append(lang)
    return rule_dict


def linguify_rule(production_list: List[Production], rule_dict: RuleDict) -> Language:
    production_langs = []
    for production in production_list:
        lang = linguify_production(production, rule_dict)
        production_langs.append(lang)
    return alt(*production_langs)


def linguify_production(production: Production, rule_dict: RuleDict) -> Language:
    if isinstance(production, RuleAliasProduction):
        return linguify_rule_alias_production(production, rule_dict)
    elif isinstance(production, NamedProduction):
        return linguify_named_production(production)
    else:
        raise LinguifierError(f"Unsupported production type: {type(production)}")


def linguify_rule_alias_production(production: RuleAliasProduction, rule_dict: RuleDict) -> Language:
    return make_rule_literal(production.name, rule_dict)


def linguify_named_production(production: NamedProduction) -> Language:
    # TODO: make AST object
    # TODO: create language from production parts
    ...


def make_rule_literal(rule_name: str, rule_dict: RuleDict) -> RuleLiteral:
    return RuleLiteral(rule_name, rule_dict)
