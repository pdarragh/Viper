from viper.lexer import lex_line

import cmd


class InteractiveLexerException(Exception):
    def __init__(self, output: str):
        self.output = output


class InteractiveLexer(cmd.Cmd):  # pragma: no cover
    prompt = 'viper_lex> '

    def default(self, line):
        lexemes = lex_line(line)
        print(lexemes)

    def do_exit(self, arg):
        """Exit the interactive lexer."""
        raise InteractiveLexerException(output='exit')

    def do_quit(self, arg):
        """Quit the interactive lexer."""
        raise InteractiveLexerException(output='quit')

    def cmdloop(self, intro=None):
        try:
            super().cmdloop(intro=intro)
        except InteractiveLexerException:
            return
        except KeyboardInterrupt:
            print('\b\bexit')
            return
