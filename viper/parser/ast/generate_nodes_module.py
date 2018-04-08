from ..grammar_parsing.parse_grammar import parse_grammar_file
from ..grammar_parsing.production import *
from ..grammar_parsing.production_part import *

from collections import defaultdict
from typing import Dict, List, Optional, Tuple


# TODO: Parameters most be processed prior to line generation so lifting can occur.
# TODO: Need to handle special tokens such as NAME, CLASS, and NUMBER.
    
    
# Three levels:
#
#   1. Rules that are superclasses of other rules (through aliasing).
#   2. Rules that are superclasses only of productions.
#   3. Productions.
#
# Classes in (1) must be written first, then (2), then (3).

Param = Tuple[str, Optional[str]]


def generate_from_grammar_file(grammar_filename: str, output_filename: str):
    text = ASTNodeGenerator(grammar_filename).generate_text()
    with open(output_filename, 'w') as of:
        of.write(text)


class Arg:
    def __init__(self, name: Optional[str], type: Optional[str], wrappers=None):
        self.name = name
        self.type = type
        if wrappers:
            self.wrappers = wrappers
        else:
            self.wrappers = []


class ASTNodeGenerator:
    BASE_AST_CLASS_NAME = 'AST'

    def __init__(self, filename: str):
        self.tree = None
        self.parsed_rules = parse_grammar_file(filename)
        self.build_rule_tree(self.parsed_rules)
        for rule, production_list in self.parsed_rules.items():
            if len(production_list) == 1:
                self.make_ast_node_class_from_single_production(rule, production_list[0])
            else:
                self.make_ast_node_classes_from_production_list(rule, production_list)

    def generate_text(self) -> str:
        # Add the header.
        lines = [
            "# This module was automatically generated.",
            "",
            "from typing import List, Optional",
            "",
            "",
        ]
        # Set the depths of the nodes to accommodate parameters.
        from itertools import chain
        queue = [self.tree.root]
        while queue:
            node = queue.pop(0)
            node.depth = max(chain([0], (other.depth for other in chain(node.parents, map(lambda n: self.tree[n], node.params))))) + 1
            queue += node.children
        # Organize nodes by depth in the tree.
        tiers = defaultdict(list)
        queue = [self.tree.root]
        while queue:
            node = queue.pop(0)
            tiers[node.depth].append(node)
            queue += node.children
        # Iterating by tier, add nodes' lines.
        for depth in sorted(tiers.keys()):
            tier = tiers[depth]
            for node in tier:
                lines += node.lines
                lines += ["", ""]
        # Remove extra blank line at the end and return.
        del(lines[-1])
        return '\n'.join(lines)

    class ClassTree:
        def __init__(self):
            self._nodes = {}
            root = ASTNodeGenerator.ClassTreeNode(ASTNodeGenerator.BASE_AST_CLASS_NAME)
            root.lines = [
                'class ' + root.name + ':',
                '    pass'
            ]
            self._nodes[ASTNodeGenerator.BASE_AST_CLASS_NAME] = root
            self.root = root

        def __getitem__(self, item):
            return self._nodes[item]

        def __setitem__(self, key, value):
            if key in self._nodes:
                raise RuntimeError  # TODO: Replace with custom error.
            self._nodes[key] = value

        def add(self, child_name: str, parent_name: str):
            parent_node = self[parent_name]
            if child_name in self._nodes:
                child_node = self[child_name]
                child_node.parents.append(parent_node)
                child_node.depth = max(parent.depth for parent in child_node.parents)
                parent_node.children.append(child_node)
            else:
                child_node = ASTNodeGenerator.ClassTreeNode(child_name)
                child_node.depth = parent_node.depth + 1
                child_node.parents.append(parent_node)
                parent_node.children.append(child_node)
                self[child_name] = child_node

        def add_to_root(self, child_name: str):
            self.add(child_name, self.root.name)

    class ClassTreeNode:
        def __init__(self, name: str):
            self.name = name
            self.parents = []
            self.children = []
            self.lines = []
            self.depth = 0
            self.params = []

        def __repr__(self):
            return self.name

    def build_rule_tree(self, parsed_rules: Dict[str, List[Production]]):
        self.tree = ASTNodeGenerator.ClassTree()

        rules = set()                   # All rules.
        aliases = defaultdict(list)     # Map: aliased-rule -> [parent rules]
        productions = {}                # Map: prod-name -> parent rule

        for rule, production_list in parsed_rules.items():
            rules.add(rule)
            solo = False
            if len(production_list) == 1:
                solo = True
            for production in production_list:
                if isinstance(production, RuleAliasProduction):
                    aliases[production.name].append(rule)
                elif isinstance(production, NamedProduction):
                    if not solo:
                        productions[production.name] = rule
                else:
                    raise RuntimeError  # TODO: Replace with custom class.

        for rule in rules:
            self.tree.add_to_root(rule)
        for alias, parents in aliases.items():
            node = self.tree[alias]
            for parent in parents:
                parent_node = self.tree[parent]
                node.parents.append(parent_node)
                parent_node.children.append(node)
            node.depth = max(parent.depth for parent in node.parents)
        for production, parent in productions.items():
            self.tree.add(production, parent)

    def make_ast_node_class_from_single_production(self, rule: str, production: Production):
        if isinstance(production, RuleAliasProduction):
            # This was handled in pre-processing.
            return
        elif isinstance(production, NamedProduction):
            self.make_ast_node_class(rule, production.parts)
        else:
            raise RuntimeError  # TODO: Replace with custom error.

    def make_ast_node_classes_from_production_list(self, rule: str, production_list: List[Production]):
        # Make the base class for these productions to inherit from.
        self.make_ast_node_class(rule, [])
        # Now create each child class.
        for production in production_list:
            if isinstance(production, NamedProduction):
                class_name = production.name
                self.make_ast_node_class(class_name, production.parts)

    def make_ast_node_class(self, class_rule_name: str, parts: List[ProductionPart]):
        node = self.tree[class_rule_name]
        lines = node.lines
        class_name = self.convert_name_to_class_name(class_rule_name)
        superclasses = ', '.join([self.convert_name_to_class_name(parent.name) for parent in node.parents])

        has_args = False
        params = [('self', None)]
        for part in parts:
            arg = self.get_arg_from_production_part(part)
            if arg is None or arg.name is None:
                continue
            if arg.type is None:
                arg_type = None
            else:
                has_args = True
                node.params.append(arg.type)
                arg_type = self.convert_name_to_class_name(arg.type)
                for wrapper in reversed(arg.wrappers):
                    arg_type = wrapper + '[' + arg_type + ']'
            pair = (arg.name, arg_type)
            params.append(pair)

        def param_to_str(param: Param) -> str:
            param_name, param_type = param
            return param_name if param_type is None else param_name + ": " + self.convert_name_to_class_name(param_type)

        joined_params = ', '.join(map(param_to_str, params))
        lines.append(f"class {class_name}({superclasses}):")
        if has_args:
            lines.append(f"    def __init__({joined_params}):")
            for name in (name for name, _ in params if name != 'self'):
                lines.append(f"        self.{name} = {name}")
        else:
            lines.append(f"    pass")

    def get_arg_from_production_part(self, part: ProductionPart) -> Optional[Arg]:
            if isinstance(part, LiteralPart):
                return None
            elif isinstance(part, SpecialPart):
                return None
            elif isinstance(part, RulePart):
                return Arg(None, part.name)
            elif isinstance(part, RepeatPart):
                part_arg = self.get_arg_from_production_part(part.part)
                if part_arg is None:
                    return None
                arg = Arg(part_arg.name, part_arg.type, part_arg.wrappers)
                arg.wrappers.append('List')
                return arg
            elif isinstance(part, SeparatedRepeatPart):
                part_arg = self.get_arg_from_production_part(part.rule)
                if part_arg is None:
                    return None
                arg = Arg(part_arg.name, part_arg.type, part_arg.wrappers)
                arg.wrappers.append('List')
                return arg
            elif isinstance(part, OptionPart):
                part_arg = self.get_arg_from_production_part(part.part)
                if part_arg is None:
                    return None
                arg = Arg(part_arg.name, part_arg.type, part_arg.wrappers)
                arg.wrappers.append('Optional')
                return arg
            elif isinstance(part, ParameterPart):
                part_arg = self.get_arg_from_production_part(part.part)
                if part_arg is None:
                    return Arg(part.name, None)
                return Arg(part.name, part_arg.type, part_arg.wrappers)
            elif isinstance(part, LiftedParameterPart):
                ...
            else:
                raise RuntimeError(f"Unexpected production part type: {type(part)}")  # TODO: Replace with custom error.

    def convert_name_to_class_name(self, name: str) -> str:
        if name[0].isupper():
            return name
        return ''.join(map(lambda s: s.title(), name.split('_')))
