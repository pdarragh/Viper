#!/usr/bin/env python3

from viper.interactive.lexer import InteractiveLexer


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-L', '--interactive-lexer', action='store_true', help='runs just the lexer in an interactive mode')
    args = parser.parse_args()

    if args.interactive_lexer:
        InteractiveLexer().cmdloop()
