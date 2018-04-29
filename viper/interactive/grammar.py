import viper.lexer as vl
import viper.parser as vp

import cmd


class InteractiveGrammarException(Exception):
    def __init__(self, output: str):
        self.output = output


class InteractiveGrammar(cmd.Cmd):  # pragma: no cover
    prompt = 'viper_ast> '

    def __init__(self, rule: str, multiline: bool):
        super().__init__()
        self.rule = rule
        self.multiline = multiline
        self.lines = []
        self.base_prompt = f'viper_sppf | {rule}> '
        self.cont_prompt = (' ' * (len(self.base_prompt) - 5)) + '...> '
        self.prompt = self.base_prompt
        self.continuing = False

    def default(self, line):
        if self.multiline:
            self._multiple_lines(line)
        else:
            self._single_line(line)

    def _single_line(self, line):
        if not line:
            return
        lexemes = vl.lex_line(line)
        self.parse(lexemes)

    def _multiple_lines(self, line):
        if line:
            if len(self.lines) == 0:
                self.prompt = self.cont_prompt  # TODO: Adjust to use self.continuing
            self.continuing = True
            self.lines.append(line)
            return
        self.prompt = self.base_prompt
        print("[")
        for line in self.lines:
            print("    " + line)
        print("]")
        lexemes = vl.lex_lines('\n'.join(self.lines))
        del(lexemes[-1])  # Remove the EndMarker.
        outputs = []
        curr_line = []
        for lexeme in lexemes:
            if isinstance(lexeme, vl.NewLine):
                outputs.append(' '.join(map(repr, curr_line)))
                curr_line = []
            curr_line.append(lexeme)
        outputs.append(' '.join(map(repr, curr_line)))
        print('\n'.join(outputs))
        self.lines = []
        self.parse(lexemes)

    def parse(self, lexemes):
        parse = vp.GRAMMAR.parse_rule(self.rule, lexemes)
        if isinstance(parse, vp.NoParse):
            print("No parse.")
        elif isinstance(parse, vp.SingleParse):
            print(vp.ast_to_string(parse.ast))
        elif isinstance(parse, vp.MultipleParse):
            print(f"Produced {len(parse.parses)} parses.")
            for i, ast in enumerate(parse.asts):
                print(f"Parse {i}:")
                print(vp.ast_to_string(ast))
        else:
            raise RuntimeError(f"Invalid return result: {parse}")

    def emptyline(self):
        return self.default('')

    def parseline(self, line):
        if self.continuing:
            line = line.rstrip()
        else:
            line = line.strip()
        if not line:
            return None, None, line
        elif line[0] == '?':
            line = 'help ' + line[1:]
        elif line[0] == '!':
            if hasattr(self, 'do_shell'):
                line = 'shell ' + line[1:]
            else:
                return None, None, line
        i, n = 0, len(line)
        while i < n and line[i] in self.identchars: i = i+1
        cmd, arg = line[:i], line[i:].strip()
        return cmd, arg, line

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
