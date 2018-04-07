from ..grammar_parsing.parse_grammar import parse_grammar_file
from ..grammar_parsing.production import *
from ..grammar_parsing.production_part import *

from typing import Dict, List, Optional, Tuple


# TODO: Address invariant: parameter lifting can only be applied to monoproduction rules.


def generate_from_grammar_file(grammar_filename: str, output_filename: str):
    ASTNodeGenerator(grammar_filename).generate(output_filename)


class ASTNodeGenerator:
    BASE_AST_CLASS_NAME = 'AST'

    def __init__(self, filename: str):
        self.lines: List[str] = []
        self.class_names: Dict[str, str] = {}
        self.rule_superclasses: Dict[str, str] = {}
        self.production_superclasses: Dict[str, str] = {}
        self.initialize()
        parsed_rules = parse_grammar_file(filename)
        self.pre_process_rules(parsed_rules)
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
        lines = '\n'.join(self.lines)
        lines = lines.format(**self.class_names)
        with open(output_filename, 'w') as of:
            of.write(lines)

    def pre_process_rules(self, parsed_rules: Dict[str, List[Production]]):
        for rule, production_list in parsed_rules.items():
            rule_class_name = self.convert_rule_name_to_class(rule)
            self.class_names[rule] = rule_class_name
            if len(production_list) == 1:
                continue
            for production in production_list:
                self.pre_process_production(rule, production)

    def pre_process_production(self, rule: str, production: Production):
        if isinstance(production, RuleAliasProduction):
            self.rule_superclasses[production.name] = rule
        elif isinstance(production, NamedProduction):
            self.production_superclasses[production.name] = rule
        else:
            raise RuntimeError  # TODO: Replace with custom error.

    def make_ast_node_class_from_single_production(self, rule: str, production: Production):
        class_name = self.convert_rule_name_to_class(rule)
        if isinstance(production, RuleAliasProduction):
            # This was handled in pre-processing.
            return
        elif isinstance(production, NamedProduction):
            args = self.get_args_from_production(production)
            self.make_ast_node_class(class_name, self.BASE_AST_CLASS_NAME, args)
        else:
            raise RuntimeError  # TODO: Replace with custom error.

    def make_ast_node_classes_from_production_list(self, rule: str, production_list: List[Production]):
        # Make the base class for these productions to inherit from.
        superclass_name = self.convert_rule_name_to_class(rule)
        superclass_base_class = self.rule_superclasses.get(rule, self.BASE_AST_CLASS_NAME)
        self.make_ast_node_class(superclass_name, superclass_base_class, [])
        # Now create each child class.
        for production in production_list:
            if isinstance(production, NamedProduction):
                class_name = production.name
                args = self.get_args_from_production(production)
                self.make_ast_node_class(class_name, superclass_name, args)

    def get_args_from_production(self, production: NamedProduction) -> List[Tuple[str, str]]:
        args: List[Tuple[str, str]] = []
        for part in production.parts:
            if isinstance(part, ParameterPart):
                if isinstance(part.part, RulePart):
                    type = part.part.name
                else:
                    type = None
                pair = (part.name, type)
                args.append(pair)
            elif isinstance(part, LiftedParameterPart):
                ...
            else:
                continue
        return args

    def make_ast_node_class(self, class_name: str, superclass: Optional[str], args: List[Tuple[str, str]]):
        if superclass is None:
            inheritance = ''
        else:
            inheritance = '(' + superclass + ')'
        self.add_line(f"class {class_name}{inheritance}:")
        if args:
            params = ', '.join(name + (": {" + type + "}" if type is not None else "") for name, type in args)
            self.add_line(f"    def __init__(self, {params}):")
            for name, _ in args:
                self.add_line(f"        self.{name} = {name}")
        else:
            self.add_line("    pass")
        self.add_line("")
        self.add_line("")

    def convert_rule_name_to_class(self, rule: str) -> str:
        return ''.join(map(lambda s: s.title(), rule.split('_')))

    def add_line(self, line: str):
        self.lines.append(line)
