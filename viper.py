#!/usr/bin/env python3

from viper.interactive import *
from viper.interpreter import start_eval
from viper.lexer import lex_file, NewLine
from viper.parser import *

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--lex-file', help='produces lexemes for given file input')
    parser.add_argument('-s', '--sppf-file', help='produces SPPF for given input file')
    parser.add_argument('-p', '--parse-file', help='produces AST for given input file')
    parser.add_argument('file', nargs='?', help='file to interpret')
    args = parser.parse_args()

    if args.lex_file:
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
    elif args.sppf_file:
        lexemes = lex_file(args.file_sppf)
        sppf = GRAMMAR.sppf_from_rule(lexemes)
        print(sppf)
    elif args.parse_file:
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
    elif args.file:
        lexemes = lex_file(args.file)
        parse = GRAMMAR.parse_file(lexemes)
        if isinstance(parse, NoParse):
            print(f"Could not parse file: {args.file}")
        elif isinstance(parse, SingleParse):
            start_eval(parse.ast)
        else:
            print(f"Ambiguous parse in file: {args.file}")
    else:
        InteractiveInterpreter().cmdloop()
