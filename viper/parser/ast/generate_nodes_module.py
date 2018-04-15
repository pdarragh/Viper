from .class_tree import build_class_tree
from ..grammar_parsing.production import Production

from typing import Dict, List


def generate_nodes_from_parsed_rules(parsed_rules: Dict[str, List[Production]], output_filename: str):
    text = generate_text_from_parsed_rules(parsed_rules)
    with open(output_filename, 'w') as of:
        of.write(text)


def generate_text_from_parsed_rules(parsed_rules: Dict[str, List[Production]]) -> str:
    tree = build_class_tree(parsed_rules)
    text = tree.generate_text()
    return text
