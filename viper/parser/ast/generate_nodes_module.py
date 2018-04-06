from ..grammar_parsing.parse_grammar import parse_grammar_file
from ..grammar_parsing.production import *
from ..grammar_parsing.production_part import *

from typing import List, Optional


def generate_from_grammar_file(grammar_filename: str, output_filename: str):
    ASTNodeGenerator(grammar_filename).generate(output_filename)


class ASTNodeGenerator:
    BASE_AST_CLASS_NAME = 'AST'

    def __init__(self, filename: str):
        self.lines: List[str] = []
        self.initialize()
        parsed_rules = parse_grammar_file(filename)
        for rule, production_list in parsed_rules.items():
            if len(production_list) == 1:
                self.make_ast_node_class_from_single_production(rule, production_list[0])
            else:
                self.make_ast_node_classes_from_production_list(rule, production_list)

    def initialize(self):
        self.add_line("# This file was automatically generated.")
        self.add_line("")
        self.add_line("")
        self.add_line("class AST:")
        self.add_line("    pass")
        self.add_line("")
        self.add_line("")

    def generate(self, output_filename: str):
        with open(output_filename, 'w') as of:
            of.writelines(self.lines)

    def make_ast_node_class_from_single_production(self, rule: str, production: Production):
        class_name = self.convert_rule_name_to_class(rule)
        if isinstance(production, RuleAliasProduction):
            # If the sole production is an alias, we give a type alias.
            alias_name = self.convert_rule_name_to_class(production.name)
            self.add_line(f"{class_name} = {alias_name}")
            self.add_line("")
            self.add_line("")
        elif isinstance(production, NamedProduction):
            args = self.get_args_from_production(production)
            self.make_ast_node_class(class_name, self.BASE_AST_CLASS_NAME, args)
        else:
            raise RuntimeError  # TODO: Replace with custom error.

    def make_ast_node_classes_from_production_list(self, rule: str, production_list: List[Production]):
        alias_instances = map(lambda p: isinstance(p, RuleAliasProduction), production_list)
        if any(alias_instances):
            if all(alias_instances):
                # No type aliases are created because we cannot guarantee anything about the aliases' types.
                return
            else:
                # We don't support mix-and-match with NamedProductions and RuleAliasProductions.
                raise RuntimeError  # TODO: Replace with custom error.
        # Make the base class for these productions to inherit from.
        base_class_name = self.convert_rule_name_to_class(rule)
        self.make_ast_node_class(base_class_name, self.BASE_AST_CLASS_NAME, [])
        # Now create each child class.
        for production in production_list:
            assert isinstance(production, NamedProduction)
            class_name = self.convert_rule_name_to_class(production.name)
            args = self.get_args_from_production(production)
            self.make_ast_node_class(class_name, base_class_name, args)

    def get_args_from_production(self, production: NamedProduction) -> List[str]:
        args: List[str] = []
        for part in production.parts:
            if isinstance(part, ParameterPart):
                args.append(part.name)
            elif isinstance(part, LiftedParameterPart):
                ...
            else:
                continue
        return args

    def make_ast_node_class(self, class_name: str, superclass: Optional[str], args: List[str]):
        if superclass is None:
            inheritance = ''
        else:
            inheritance = '(' + superclass + ')'
        self.add_line(f"class {class_name}{inheritance}:")
        if args:
            params = ', '.join(args)
            self.add_line(f"    def __init__(self, {params}):")
            for arg in args:
                self.add_line(f"        self.{arg} = {arg}")
        else:
            self.add_line("    pass")
        self.add_line("")
        self.add_line("")

    def convert_rule_name_to_class(self, rule: str) -> str:
        return ''.join(map(lambda s: s.title(), rule.split('_')))

    def add_line(self, line: str):
        self.lines.append(line + '\n')
