from ..grammar_parsing.parse_grammar import parse_grammar_file
from ..grammar_parsing.production import *
from ..grammar_parsing.production_part import *

from collections import defaultdict
from itertools import chain
from typing import Dict, List, Optional, Tuple


Param = Tuple[str, Optional[str], Optional[str]]


def generate_nodes_from_grammar_file(grammar_filename: str, output_filename: str):
    text = ASTNodeGenerator(grammar_filename).generate_text()
    with open(output_filename, 'w') as of:
        of.write(text)


def convert_name_to_class_name(name: str) -> str:
    if name[0].isupper():
        return name
    return ''.join(map(lambda s: s.title(), name.split('_')))


class Arg:
    def __init__(self, name: Optional[str], type_: Optional[str], wrappers=None):
        self.name = name
        self.type = type_
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
        self.adjust_node_depths()

    def adjust_node_depths(self):
        # Set the depths of the nodes to accommodate parameters. Repeat until no updates are performed.
        # TODO: How likely is it that this will repeat many times? Should a fix-point be computed differently?
        needs_update = True
        while needs_update:
            needs_update = False
            queue = [self.tree.root]
            while queue:
                node = queue.pop(0)
                new_depth = max(chain([node.depth], (parent.depth + 1 for parent in node.parents)))
                new_depth = max(chain([new_depth],
                                      (self.tree[param].depth + 1
                                       for _, param, _ in node.params if param is not None)))
                if new_depth > node.depth:
                    node.depth = new_depth
                    needs_update = True
                queue += node.children

    def generate_text(self) -> str:
        # Add the header.
        lines = [
            "# This module was automatically generated.",
            "",
            "from typing import List, Optional",
            "",
            "",
        ]
        # Organize nodes by depth in the tree without including duplicates.
        tiers = defaultdict(set)
        queue = [self.tree.root]
        while queue:
            node = queue.pop(0)
            tiers[node.depth].add(node)
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
            if child_name in self._nodes:
                raise RuntimeError  # TODO: Replace with custom error.
            if parent_name not in self._nodes:
                raise RuntimeError  # TODO: Replace with custom error.
            parent_node = self[parent_name]
            child_node = ASTNodeGenerator.ClassTreeNode(child_name)
            child_node.parents.append(parent_node)
            parent_node.children.append(child_node)
            child_node.depth = parent_node.depth + 1
            self[child_name] = child_node

        def add_to_root(self, child_name: str):
            self.add(child_name, self.root.name)

    class ClassTreeNode:
        def __init__(self, name: str):
            self.name = name
            self.parents: List[ASTNodeGenerator.ClassTreeNode] = []
            self.children: List[ASTNodeGenerator.ClassTreeNode] = []
            self.lines: List[str] = []
            self.params: List[Param] = []
            self.depth = 0

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
            self.tree.add_to_root(convert_name_to_class_name(rule))
        for alias, parents in aliases.items():
            node = self.tree[convert_name_to_class_name(alias)]
            node.parents = []
            for parent in parents:
                parent_node = self.tree[convert_name_to_class_name(parent)]
                node.parents.append(parent_node)
                parent_node.children.append(node)
            node.depth = max(parent.depth for parent in node.parents)
        for production, parent in productions.items():
            self.tree.add(convert_name_to_class_name(production), convert_name_to_class_name(parent))

    def make_ast_node_class_from_single_production(self, rule: str, production: Production):
        if isinstance(production, RuleAliasProduction):
            # This was handled in pre-processing.
            return
        elif isinstance(production, NamedProduction):
            class_name = convert_name_to_class_name(rule)
            self.process_parameters(class_name, production.parts)
            self.make_ast_node_class(class_name)
        else:
            raise RuntimeError  # TODO: Replace with custom error.

    def make_ast_node_classes_from_production_list(self, rule: str, production_list: List[Production]):
        # Make the base class for these productions to inherit from.
        self.make_ast_node_class(convert_name_to_class_name(rule))
        # Now create each child class.
        for production in production_list:
            if isinstance(production, NamedProduction):
                class_name = convert_name_to_class_name(production.name)
                self.process_parameters(class_name, production.parts)
                self.make_ast_node_class(class_name)
            elif isinstance(production, RuleAliasProduction):
                continue
            else:
                raise RuntimeError  # TODO: Replace with custom error.

    def process_parameters(self, class_name: str, parts: List[ProductionPart]):
        node = self.tree[class_name]
        for part in parts:
            arg = self.get_arg_from_production_part(part)
            if arg is None or arg.name is None:
                continue
            if arg.type is None:
                param = (arg.name, None, 'str')
            else:
                base_arg_type = convert_name_to_class_name(arg.type)
                arg_type = base_arg_type
                for wrapper in reversed(arg.wrappers):
                    arg_type = wrapper + '[' + base_arg_type + ']'
                param = (arg.name, base_arg_type, arg_type)
            node.params.append(param)

    def make_ast_node_class(self, class_name: str):
        node = self.tree[class_name]
        lines = node.lines
        superclasses = ', '.join([parent.name for parent in node.parents])

        def param_to_str(param: Param) -> str:
            param_name, _, param_type = param
            return param_name if param_type is None else param_name + ": " + param_type

        has_params = len(node.params) > 0
        params = [('self', None, None)] + node.params

        lines.append(f"class {class_name}({superclasses}):")
        if has_params:
            joined_params = ', '.join(map(param_to_str, params))
            lines.append(f"    def __init__({joined_params}):")
            for name in (name for name, _, _ in params if name != 'self'):
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
            else:
                raise RuntimeError(f"Unexpected production part type: {type(part)}")  # TODO: Replace with custom error.

