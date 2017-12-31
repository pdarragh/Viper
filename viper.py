#!/usr/bin/env python3

from viper.interactive import *


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-L', '--interactive-lexer', action='store_true', help='lexes input')
    parser.add_argument('-S', '--interactive-sppf', action='store_true', help='lexes input and produces SPPF')
    args = parser.parse_args()

    if args.interactive_lexer:
        InteractiveLexer().cmdloop()
    elif args.interactive_sppf:
        InteractiveSPPF().cmdloop()
