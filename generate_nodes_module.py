#!/usr/bin/env python3

from viper.formal_grammar import GRAMMAR_FILE
from viper.parser.ast.generate_nodes_module import generate_text_from_parsed_rules
from viper.parser.grammar_parsing.parse_grammar import parse_grammar_file

from os.path import dirname, join


basedir = dirname(__file__)
output = join(basedir, 'viper', 'parser', 'ast', 'nodes.py')


def generate_nodes_module():
    parsed_rules = parse_grammar_file(GRAMMAR_FILE)
    text = generate_text_from_parsed_rules(parsed_rules)
    with open(output, 'w') as of:
        of.write(text)


if __name__ == '__main__':
    generate_nodes_module()
