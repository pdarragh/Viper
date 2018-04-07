from ..grammar_parsing.parse_grammar import parse_grammar_file
from ..grammar_parsing.production import *
from ..grammar_parsing.production_part import *

from collections import defaultdict
from typing import Dict, List, Optional, Tuple


# TODO: Address invariant: parameter lifting can only be applied to monoproduction rules.
    
    
# Three levels:
#
#   1. Rules that are superclasses of other rules (through aliasing).
#   2. Rules that are superclasses only of productions.
#   3. Productions.
#
# Classes in (1) must be written first, then (2), then (3).


Arg = Tuple[str, Optional[str]]
ArgList = List[Arg]


class ASTNodeGenerator:
    BASE_AST_CLASS_NAME = 'AST'

    def __init__(self, filename: str):
        self.tree = None
        parsed_rules = parse_grammar_file(filename)
        self.build_rule_tree(parsed_rules)
        for rule, production_list in parsed_rules.items():
            if len(production_list) == 1:
                self.make_ast_node_class_from_single_production(rule, production_list[0])
            else:
                self.make_ast_node_classes_from_production_list(rule, production_list)

    class ClassTree:
        def __init__(self):
            self._nodes = {}
            root = ASTNodeGenerator.ClassTreeNode('AST')
            root.lines = [
                'class AST:',
                '    pass'
            ]
            self._nodes['AST'] = root
            self.root = root

        def __getitem__(self, item):
            return self._nodes[item]

        def __setitem__(self, key, value):
            if key in self._nodes:
                raise RuntimeError  # TODO: Replace with custom error.
            self._nodes[key] = value

    class ClassTreeNode:
        def __init__(self, name: str):
            self.name = name
            self.parents = []
            self.children = []
            self.lines = []

        def add_new_child(self, child_name: str):
            node = ASTNodeGenerator.ClassTreeNode(child_name)
            node.parents.append(self)
            self.children.append(node)
            return node

    def build_rule_tree(self, parsed_rules: Dict[str, List[Production]]):
        self.tree = ASTNodeGenerator.ClassTree()

        rules = set()                   # All rules.
        aliases = defaultdict(list)     # Map: aliased-rule -> [parent rules]
        productions = {}                # Map: prod-name -> parent rule

        for rule, production_list in parsed_rules.items():
            rules.add(rule)
            for production in production_list:
                if isinstance(production, RuleAliasProduction):
                    aliases[production.name].append(rule)
                elif isinstance(production, NamedProduction):
                    productions[production.name] = rule
                else:
                    raise RuntimeError

        for rule in rules:
            self.tree[rule] = self.tree.root.add_new_child(rule)
        for alias, parents in aliases.items():
            node = self.tree[alias]
            for parent in parents:
                parent_node = self.tree[parent]
                node.parents.append(parent_node)
                parent_node.children.append(node)
        for production, parent in productions.items():
            parent_node = self.tree[parent]
            self.tree[production] = parent_node.add_new_child(production)

    def make_ast_node_class_from_single_production(self, rule: str, production: Production):
        if isinstance(production, RuleAliasProduction):
            # This was handled in pre-processing.
            return
        elif isinstance(production, NamedProduction):
            args = self.get_args_from_production(production)
            self.make_ast_node_class(rule, args)
        else:
            raise RuntimeError  # TODO: Replace with custom error.

    def make_ast_node_classes_from_production_list(self, rule: str, production_list: List[Production]):
        # Make the base class for these productions to inherit from.
        self.make_ast_node_class(rule, [])
        # Now create each child class.
        for production in production_list:
            if isinstance(production, NamedProduction):
                class_name = production.name
                args = self.get_args_from_production(production)
                self.make_ast_node_class(class_name, args)

    def get_args_from_production(self, production: NamedProduction) -> List[Arg]:
        args: List[Arg] = []
        for part in production.parts:
            if isinstance(part, ParameterPart):
                if isinstance(part.part, RulePart):
                    arg_type = part.part.name
                else:
                    arg_type = None
                pair = (part.name, arg_type)
                args.append(pair)
            elif isinstance(part, LiftedParameterPart):
                ...
            else:
                continue
        return args

    def make_ast_node_class(self, class_rule_name: str, args: List[Arg]):
        node = self.tree[class_rule_name]
        lines = node.lines
        class_name = self.convert_name_to_class_name(class_rule_name)
        superclasses = ', '.join([self.convert_name_to_class_name(parent.name) for parent in node.parents])

        def param_from_arg(arg: Arg) -> str:
            arg_name, arg_type = arg
            return arg_name if arg_type is None else arg_name + ": {" + arg_type + "}"

        params = ', '.join(map(param_from_arg, [('self', None)] + args))
        lines.append(f"class {class_name}({superclasses}):")
        if args:
            lines.append(f"    def__init__({params}):")
            for name, _ in args:
                lines.append(f"        self.{name} = {name}")
        else:
            lines.append(f"    pass")

    def convert_name_to_class_name(self, name: str) -> str:
        if name[0].isupper():
            return name
        return ''.join(map(lambda s: s.title(), name.split('_')))
