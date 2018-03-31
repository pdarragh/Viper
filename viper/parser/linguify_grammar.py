from .ast import ASTNode
from .grammar_parsing.parse_grammar import parse_grammar_file
from .grammar_parsing.production import *
from .grammar_parsing.production_part import *
from .grammar_parsing.tokenize.special_tokens import SPECIAL_TOKENS
from .languages import *

from viper.error import ViperError
from viper.lexer import Lexeme

from typing import Any, Callable, Dict, List, NamedTuple, Optional


RuleDict = Dict[str, Language]
ParamFunc = Callable[[SPPF], Any]
PartTuple = NamedTuple('PartTuple', [('lang', Language), ('name', Optional[str])])


class LinguifierError(ViperError):
    pass


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
    param_names: List[Optional[str]] = []
    part_langs = []
    for part in production.parts:
        part = linguify_production_part(part, rule_dict)
        part_langs.append(part.lang)
        param_names.append(part.name)
    prod_lang = concat(*part_langs)
    prod_lang = make_ast_red(prod_lang, production.name, param_names)
    return prod_lang


class ASTNodeRedFunc(RedFunc):
    def __init__(self, name: str, param_names: List[Optional[str]]):
        self.name = name
        self.param_names = param_names

    def make_nice_string(self, start_column: int) -> str:
        return self.name

    def __call__(self, sppf: SPPF) -> SPPF:
        """
        The SPPF for a production will look something like:

            (pair (char ...)
                  (pair (char ...)
                        (pair (pair (...
                                     ...)
                              (pair (char ...)
                                    (char ...)))))

        :param sppf: the SPPF for the production we expect to produce (already parse_null'ed)
        :return: a simplified SPPF
        """
        params = {}
        curr = sppf
        for name in self.param_names:
            if not curr:
                # There was nothing for the parameter to match.
                return SPPF()
            if len(curr) > 1:
                # TODO: Not sure if this is correct.
                raise LinguifierError(f"SPPF has too many children: {curr}")
            child = curr[0]
            if isinstance(child, ParseTreeEmpty):
                return SPPF()
            elif isinstance(child, ParseTreeEps):
                if name is None:
                    curr = SPPF()
                else:
                    params[name] = None
            elif isinstance(child, ParseTreeChar):
                if name is not None:
                    params[name] = child.token
                curr = SPPF()
            elif isinstance(child, ParseTreePair):
                param_sppf = child.left
                if len(param_sppf) != 1:
                    raise LinguifierError(f"Invalid child SPPF: {param_sppf}")
                if name is not None:
                    # TODO: This should be checked more safely.
                    param_child = param_sppf[0]
                    if isinstance(param_child, ParseTreeChar):
                        params[name] = param_child.token
                    else:
                        raise LinguifierError(f"Invalid child SPPF child: {param_child}")
                curr = child.right
            else:
                raise LinguifierError("Invalid child node.")
        return SPPF(ParseTreeChar(ASTNode(self.name, params)))


def make_ast_red(lang: Language, name: str, param_names: List[Optional[str]]) -> Language:
    func = ASTNodeRedFunc(name, param_names)
    return red(lang, func)


def make_rule_literal(rule_name: str, rule_dict: RuleDict) -> RuleLiteral:
    return RuleLiteral(rule_name, rule_dict)


def linguify_production_part(part: ProductionPart, rule_dict: RuleDict) -> PartTuple:
    if isinstance(part, LiteralPart):
        part = literal(Lexeme(part.text))
        return PartTuple(part, None)
    elif isinstance(part, SpecialPart):
        part = literal(SPECIAL_TOKENS[part.token])
        return PartTuple(part, None)
    elif isinstance(part, RulePart):
        part = make_rule_literal(part.name, rule_dict)
        return PartTuple(part, None)
    elif isinstance(part, RepeatPart):
        inner_part = linguify_production_part(part.part, rule_dict)
        part = rep(inner_part.lang)
        return PartTuple(part, None)
    elif isinstance(part, SeparatedRepeatPart):
        inner_part = linguify_production_part(part.rule, rule_dict)
        separator_part = linguify_production_part(part.separator, rule_dict)
        part = sep_rep(separator_part.lang, inner_part.lang)
        return PartTuple(part, None)
    elif isinstance(part, OptionPart):
        inner_part = linguify_production_part(part.part, rule_dict)
        part = opt(inner_part.lang)
        return PartTuple(part, None)
    elif isinstance(part, ParameterPart):
        inner_part = linguify_production_part(part.part, rule_dict)
        return PartTuple(inner_part.lang, part.name)
    elif isinstance(part, ExpandedParameterPart):
        # TODO: Fix this.
        return linguify_production_part(part.rule, rule_dict)
    else:
        raise LinguifierError(f"Cannot linguify unknown production part: {part}")
