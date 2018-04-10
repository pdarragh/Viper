from ..grammar_parsing.production import *
from ..grammar_parsing.production_part import *

from collections import defaultdict
from itertools import chain
from typing import Dict, List, Optional, Set, Tuple


BASE_AST_CLASS_NAME = 'AST'

Param = Tuple[str, Optional[str], Optional[str]]
RuleSet = Set[str]
AliasDict = Dict[str, List[str]]
ProdDict = Dict[str, str]


class Arg:
    def __init__(self, name: Optional[str], type_: Optional[str], wrappers=None):
        self.name = name
        self.type = type_
        if wrappers is None:
            self.wrappers = []
        else:
            self.wrappers = wrappers


class ClassTree:
    def __init__(self):
        self._nodes = {}
        root = ClassTreeNode(BASE_AST_CLASS_NAME)
        root.lines = [
            'class ' + root.name + ':',
            '    pass'
        ]
        self._nodes[BASE_AST_CLASS_NAME] = root
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
        child_node = ClassTreeNode(child_name)
        child_node.parents.append(parent_node)
        parent_node.children.append(child_node)
        child_node.depth = parent_node.depth + 1
        self[child_name] = child_node

    def add_to_root(self, child_name: str):
        self.add(child_name, self.root.name)


class ClassTreeNode:
    def __init__(self, name: str):
        self.name = name
        self.parents: List[ClassTreeNode] = []
        self.children: List[ClassTreeNode] = []
        self.lines: List[str] = []
        self.params: List[Param] = []
        self.depth = 0

    def __repr__(self):
        return self.name


def build_class_tree(parsed_rules: Dict[str, List[Production]]) -> ClassTree:
    rules, aliases, productions = identify_rules_and_classes(parsed_rules)
    tree = construct_bare_tree(rules, aliases, productions)
    make_ast_nodes_from_rules(parsed_rules, tree)
    update_node_depths(tree)
    return tree


def identify_rules_and_classes(parsed_rules: Dict[str, List[Production]]) -> Tuple[RuleSet, AliasDict, ProdDict]:
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
    return rules, aliases, productions


def construct_bare_tree(rules: RuleSet, aliases: AliasDict, productions: ProdDict) -> ClassTree:
    tree = ClassTree()
    for rule in rules:
        tree.add_to_root(convert_name_to_class_name(rule))
    for alias, parents in aliases.items():
        node = tree[convert_name_to_class_name(alias)]
        node.parents = []
        for parent in parents:
            parent_node = tree[convert_name_to_class_name(parent)]
            node.parents.append(parent_node)
            parent_node.children.append(node)
        node.depth = max(parent.depth for parent in node.parents)
    for production, parent in productions.items():
        tree.add(convert_name_to_class_name(production), convert_name_to_class_name(parent))
    return tree


def make_ast_nodes_from_rules(parsed_rules: Dict[str, List[Production]], tree: ClassTree):
    for rule, production_list in parsed_rules.items():
        if len(production_list) == 1:
            make_ast_node_class_from_single_production(rule, production_list[0], tree)
        else:
            make_ast_node_classes_from_production_list(rule, production_list, tree)


def make_ast_node_class_from_single_production(rule: str, production: Production, tree: ClassTree):
    if isinstance(production, RuleAliasProduction):
        # This was handled in pre-processing.
        return
    elif isinstance(production, NamedProduction):
        class_name = convert_name_to_class_name(rule)
        process_parameters_for_class(class_name, production.parts, tree)
        make_ast_node_class(class_name, tree)
    else:
        raise RuntimeError  # TODO: Replace with custom error.


def make_ast_node_classes_from_production_list(rule: str, production_list: List[Production], tree: ClassTree):
    # Make the base class for these productions to inherit from.
    make_ast_node_class(convert_name_to_class_name(rule), tree)
    # Now create each child class.
    for production in production_list:
        if isinstance(production, NamedProduction):
            class_name = convert_name_to_class_name(production.name)
            process_parameters_for_class(class_name, production.parts, tree)
            make_ast_node_class(class_name, tree)
        elif isinstance(production, RuleAliasProduction):
            continue
        else:
            raise RuntimeError  # TODO: Replace with custom error.


def process_parameters_for_class(class_name: str, parts: List[ProductionPart], tree: ClassTree):
    node = tree[class_name]
    for part in parts:
        arg = get_arg_from_production_part(part)
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


def param_to_str(param: Param) -> str:
    param_name, _, param_type = param
    return param_name if param_type is None else param_name + ": " + param_type


def make_ast_node_class(class_name: str, tree: ClassTree):
    node = tree[class_name]
    lines = node.lines
    superclasses = ', '.join([parent.name for parent in node.parents])
    has_params = len(node.params) > 0
    params = [('self', None, None)] + node.params
    # Put the lines into the node.
    lines.append(f"class {class_name}({superclasses}):")
    if has_params:
        joined_params = ', '.join(map(param_to_str, params))
        lines.append(f"    def __init__({joined_params}):")
        for name in (name for name, _, _ in params if name != 'self'):
            lines.append(f"        self.{name} = {name}")
    else:
        lines.append(f"    pass")


def get_arg_from_production_part(part: ProductionPart) -> Optional[Arg]:
        if isinstance(part, LiteralPart):
            return None
        elif isinstance(part, SpecialPart):
            return None
        elif isinstance(part, RulePart):
            return Arg(None, part.name)
        elif isinstance(part, RepeatPart):
            part_arg = get_arg_from_production_part(part.part)
            if part_arg is None:
                return None
            arg = Arg(part_arg.name, part_arg.type, part_arg.wrappers)
            arg.wrappers.append('List')
            return arg
        elif isinstance(part, SeparatedRepeatPart):
            part_arg = get_arg_from_production_part(part.rule)
            if part_arg is None:
                return None
            arg = Arg(part_arg.name, part_arg.type, part_arg.wrappers)
            arg.wrappers.append('List')
            return arg
        elif isinstance(part, OptionPart):
            part_arg = get_arg_from_production_part(part.part)
            if part_arg is None:
                return None
            arg = Arg(part_arg.name, part_arg.type, part_arg.wrappers)
            arg.wrappers.append('Optional')
            return arg
        elif isinstance(part, ParameterPart):
            part_arg = get_arg_from_production_part(part.part)
            if part_arg is None:
                return Arg(part.name, None)
            return Arg(part.name, part_arg.type, part_arg.wrappers)
        else:
            raise RuntimeError(f"Unexpected production part type: {type(part)}")  # TODO: Replace with custom error.


def update_node_depths(tree: ClassTree):
    # Set the depths of the nodes to accommodate parameters. Repeat until no updates are performed.
    # TODO: How likely is it that this will repeat many times? Should a fix-point be computed differently?
    needs_update = True
    while needs_update:
        needs_update = False
        queue = [tree.root]
        while queue:
            node = queue.pop(0)
            new_depth = max(chain([node.depth], (parent.depth + 1 for parent in node.parents)))
            new_depth = max(chain([new_depth],
                                  (tree[param].depth + 1
                                   for _, param, _ in node.params if param is not None)))
            if new_depth > node.depth:
                node.depth = new_depth
                needs_update = True
            queue += node.children


def convert_name_to_class_name(name: str) -> str:
    if name[0].isupper():
        return name
    return ''.join(map(lambda s: s.title(), name.split('_')))
