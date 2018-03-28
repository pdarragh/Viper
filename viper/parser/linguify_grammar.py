from .grammar_parsing.parse_grammar import parse_grammar_file
from .grammar_parsing.production import *
from .grammar_parsing.production_part import *
from .grammar_parsing.tokenize.special_tokens import SPECIAL_TOKENS
from .languages import *

from viper.error import ViperError
from viper.lexer import Lexeme

from typing import Dict, List


RuleDict = Dict[str, Language]


class LinguifierError(ViperError):
    pass


class Grammar:
    def __init__(self, grammar_filename: str):
        self.file = grammar_filename
        self.rules = linguify_grammar_file(self.file)

    def parse_rule(self, rule: str, lexemes: List[Lexeme]) -> SPPF:
        lang = self.rules[rule]
        return make_sppf(lang, lexemes)


def linguify_grammar_file(filename: str) -> RuleDict:
    parsed_rules = parse_grammar_file(filename)
    rule_dict = {}
    for rule, production_list in parsed_rules.items():
        lang = linguify_rule(production_list, rule_dict)
        rule_dict[rule] = lang
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
        return linguify_named_production(production, rule_dict)
    else:
        raise LinguifierError(f"Unsupported production type: {type(production)}")


def linguify_rule_alias_production(production: RuleAliasProduction, rule_dict: RuleDict) -> Language:
    return make_rule_literal(production.name, rule_dict)


def linguify_named_production(production: NamedProduction, rule_dict: RuleDict) -> Language:
    # TODO: make AST object
    # TODO: create language from production parts
    ...
    part_langs = []
    for part in production.parts:
        lang = linguify_production_part(part, rule_dict)
        part_langs.append(lang)
    prod_lang = concat(*part_langs)
    ...
    return prod_lang


def make_rule_literal(rule_name: str, rule_dict: RuleDict) -> RuleLiteral:
    return RuleLiteral(rule_name, rule_dict)


def linguify_production_part(part: ProductionPart, rule_dict: RuleDict) -> Language:
    if isinstance(part, LiteralPart):
        return literal(Lexeme(part.text))
    elif isinstance(part, SpecialPart):
        return literal(SPECIAL_TOKENS[part.token])
    elif isinstance(part, RulePart):
        return make_rule_literal(part.name, rule_dict)
    elif isinstance(part, RepeatPart):
        return rep(linguify_production_part(part.part, rule_dict))
    elif isinstance(part, OptionPart):
        return opt(linguify_production_part(part.part, rule_dict))
    elif isinstance(part, ParameterPart):
        # TODO: Fix this.
        return linguify_production_part(part.part, rule_dict)
    elif isinstance(part, ExpandedParameterPart):
        # TODO: Fix this.
        return linguify_production_part(part.rule, rule_dict)
    elif isinstance(part, SpecialExpandedParameterPart):
        # TODO: Fix this.
        return linguify_production_part(part.rule, rule_dict)
    else:
        raise LinguifierError(f"Cannot linguify unknown production part: {part}")
