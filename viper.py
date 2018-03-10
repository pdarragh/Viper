#!/usr/bin/env python3

from viper.interactive import *
from viper.lexer import lex_file, NewLine
from viper.grammar import GRAMMAR


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-L', '--interactive-lexer', action='store_true', help='lexes input')
    parser.add_argument('-l', '--file-lexer', help='produces lexemes for given file input')
    parser.add_argument('-S', '--interactive-sppf', action='store_true', help='lexes input and produces SPPF')
    parser.add_argument('-s', '--file-sppf', help='produces SPPF for given input')
    parser.add_argument('-r', '--grammar-rule', default='single_line', help='grammar rule from which to start parsing')
    args = parser.parse_args()

    if args.interactive_lexer:
        InteractiveLexer().cmdloop()
    elif args.file_lexer:
        lexemes = lex_file(args.file_lexer)
        outputs = []
        curr_line = []
        for lexeme in lexemes:
            if isinstance(lexeme, NewLine):
                outputs.append(' '.join(map(repr, curr_line)))
                curr_line = []
            curr_line.append(lexeme)
        outputs.append(' '.join(map(repr, curr_line)))
        print('\n'.join(outputs))
    elif args.interactive_sppf:
        InteractiveSPPF(args.grammar_rule).cmdloop()
    elif args.file_sppf:
        lexemes = lex_file(args.file_sppf)
        sppf = GRAMMAR.parse_file(lexemes)
        print(sppf)
