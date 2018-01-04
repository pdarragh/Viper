from viper.grammar import *
from viper.lexer import lex_lines, LexerError

import cmd


class InteractiveSPPFException(Exception):
    def __init__(self, output: str):
        self.output = output


class InteractiveSPPF(cmd.Cmd):  # pragma: no cover
    prompt = 'viper_sppf> '

    def default(self, line):
        lexemes = lex_lines(line)
        sppf = GRAMMAR.parse_single(lexemes)
        print(sppf)

    def do_exit(self, arg):
        """Exit the interactive lexer."""
        raise InteractiveSPPFException(output='exit')

    def do_quit(self, arg):
        """Quit the interactive lexer."""
        raise InteractiveSPPFException(output='quit')

    def cmdloop(self, intro=None):
        try:
            super().cmdloop(intro=intro)
        except LexerError as e:
            print(e)
            self.cmdloop(intro=intro)
        except InteractiveSPPFException:
            return
        except KeyboardInterrupt:
            print('\b\bexit')
            return
