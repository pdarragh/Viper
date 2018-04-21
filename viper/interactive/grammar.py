import viper.lexer as vl
import viper.parser as vp

import cmd


class InteractiveGrammarException(Exception):
    def __init__(self, output: str):
        self.output = output


class InteractiveGrammar(cmd.Cmd):  # pragma: no cover
    prompt = 'viper_ast> '

    def __init__(self, rule: str):
        super().__init__()
        self.rule = rule
        self.prompt = f'viper_sppf | {rule}> '

    def default(self, line):
        lexemes = vl.lex_line(line)
        ast = vp.GRAMMAR.parse_rule(self.rule, lexemes)
        print(vp.ast_to_string(ast))

    def do_exit(self, arg):
        """Exit the interactive lexer."""
        raise InteractiveGrammarException(output='exit')

    def do_quit(self, arg):
        """Quit the interactive lexer."""
        raise InteractiveGrammarException(output='quit')

    def cmdloop(self, intro=None):
        try:
            super().cmdloop(intro=intro)
        except vl.LexerError as e:
            print(e)
            self.cmdloop(intro=intro)
        except InteractiveGrammarException:
            return
        except KeyboardInterrupt:
            print('\b\bexit')
            return
