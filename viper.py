#!/usr/bin/env python3

from viper.interactive import *
from viper.lexer import lex_file, NewLine
from viper.parser import *

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-L', '--interactive-lexer', action='store_true', help='lexes input')
    parser.add_argument('-l', '--file-lexer', help='produces lexemes for given file input')
    parser.add_argument('-S', '--interactive-sppf', action='store_true', help='lexes input and produces SPPF')
    parser.add_argument('-s', '--file-sppf', help='produces SPPF for given input file')
    parser.add_argument('-G', '--interactive-grammar', action='store_true', help='lexes input and produces AST')
    parser.add_argument('-g', '--file-grammar', help='produces AST for given input file')
    parser.add_argument('-r', '--grammar-rule', default='single_input', help='parser rule from which to start parsing')
    parser.add_argument('-m', '--multiline', action='store_true', help='enable multi-line processing in interactive mode')
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
        sppf = GRAMMAR.sppf_from_rule(lexemes)
        print(sppf)
    elif args.interactive_grammar:
        InteractiveGrammar(args.grammar_rule, args.multiline).cmdloop()
    elif args.file_grammar:
        lexemes = lex_file(args.file_grammar)
        parse = GRAMMAR.parse_file(lexemes)
        if isinstance(parse, NoParse):
            print("No parse.")
        elif isinstance(parse, SingleParse):
            print(ast_to_string(parse.ast))
        elif isinstance(parse, MultipleParse):
            print(f"Produced {len(parse.parses)} parses.")
            for i, ast in enumerate(parse.asts):
                print(f"Parse {i}:")
                print(ast_to_string(ast))
        else:
            raise RuntimeError(f"Invalid return result: {parse}")
    else:
        InteractiveInterpreter().cmdloop()
