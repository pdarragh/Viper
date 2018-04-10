from .class_tree import ClassTree, build_class_tree
from ..grammar_parsing.production import Production

from collections import defaultdict
from typing import Dict, List


def generate_nodes_from_parsed_rules(parsed_rules: Dict[str, List[Production]], output_filename: str):
    text = generate_text_from_parsed_rules(parsed_rules)
    with open(output_filename, 'w') as of:
        of.write(text)


def generate_text_from_parsed_rules(parsed_rules: Dict[str, List[Production]]) -> str:
    tree = build_class_tree(parsed_rules)
    text = generate_text(tree)
    return text


def generate_text(tree: ClassTree) -> str:
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
    queue = [tree.root]
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
