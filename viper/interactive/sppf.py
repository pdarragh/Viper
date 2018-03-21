from viper.parser import *
from viper.lexer import lex_line, LexerError, NEWLINE

import cmd


class InteractiveSPPFException(Exception):
    def __init__(self, output: str):
        self.output = output


class InteractiveSPPF(cmd.Cmd):  # pragma: no cover
    prompt = 'viper_sppf> '

    def __init__(self, rule: str):
        super().__init__()
        self.rule = rule
        self.prompt = f'viper_sppf | {rule}> '

    def default(self, line):
        lines = line.split('\\n')
        lexeme_lines = [lex_line(line) for line in lines]
        lexemes = []
        for i, ln in enumerate(lexeme_lines):
            lexemes += ln
            if i < len(lexeme_lines) - 1:
                lexemes.append(NEWLINE)
        sppf = GRAMMAR.parse_rule(self.rule, lexemes)
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
