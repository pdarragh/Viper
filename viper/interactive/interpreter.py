import viper.lexer as vl

from viper.parser import *
from viper.interpreter.interpreter import *

import cmd


SINGLE_INPUT_RULE = 'single_input'
MULTILINE_INPUT_RULE = 'stmt_block'

SINGLE_INPUT_PROMPT = '>>> '
MULTILINE_INPUT_PROMPT = '... '


class InteractiveInterpreterException(Exception):
    def __init__(self, output: str):
        self.output = output


class StopREPL(Exception):
    pass


class InteractiveInterpreter(cmd.Cmd):  # pragma: no cover
    prompt = SINGLE_INPUT_PROMPT

    def __init__(self):
        super().__init__()
        self.multiline = False
        self.lines = []
        self.env = None
        self.store = None

    def cmdloop(self, intro=None):
        cont = True
        while cont:
            try:
                super().cmdloop(intro=intro)
            except InteractiveInterpreterException as e:
                self._handle_error(f"Error: {e.output}")
            except KeyboardInterrupt:
                self._handle_error('KeyboardInterrupt')
            except StopREPL:
                cont = False
            except Exception as e:
                self._handle_error(f"Error: {str(e)}")

    def _handle_error(self, msg: str):
        print()
        print(msg)
        self.multiline = False
        self.lines = []
        self._update_prompt()

    def default(self, line: str):
        self._parse_input(line)
        self._update_prompt()

    def _parse_input(self, line: str):
        line.replace('\\', '\\\\')
        if line == 'EOF':
            raise StopREPL
        elif line == ':{':
            if self.multiline:
                raise InteractiveInterpreterException(f"Already in multiline mode.")
            else:
                # Begin multi-line processing.
                self.multiline = True
        elif line == ':}':
            if self.multiline:
                # End multi-line processing.
                self.multiline = False
                # Interpret the result.
                lines = '\n'.join(self.lines)
                lexemes = [vl.NEWLINE, vl.INDENT] + vl.lex_lines(lines)[:-1] + [vl.DEDENT]
                parse = GRAMMAR.parse_rule(MULTILINE_INPUT_RULE, lexemes)
                if isinstance(parse, NoParse):
                    raise InteractiveInterpreterException(f"Could not parse multiline input: {repr(lines)}")
                result = start_eval(parse.ast, env=self.env, store=self.store)
                self.env = result.env
                self.store = result.store
            else:
                raise InteractiveInterpreterException(f"Not currently in multiline mode.")
        else:
            split_line = line.split(maxsplit=1)
            starter = split_line[0]
            if len(split_line) == 2:
                remainder = split_line[1]
            else:
                remainder = None
            if starter in {':t', ':type'}:
                # Get type information of result.
                # TODO: Implement this.
                raise InteractiveInterpreterException(f"Type checking not supported at this time.")
            elif starter in {':e', ':env'}:
                # Get information from the current environment.
                if remainder:
                    val = self.env.get(remainder)
                    if val is None:
                        raise InteractiveInterpreterException(f"No such element in environment: {remainder}")
                    else:
                        print(f"env[{remainder}]: {val}")
                else:
                    print(self.env)
            elif starter in {':s', ':store'}:
                # Get information from the current store.
                if remainder:
                    val = self.store.get(remainder)
                    if val is None:
                        try:
                            addr = int(remainder)
                        except ValueError:
                            addr = self.env.get(remainder)
                            remainder = f'env[{remainder}]'
                        if addr is None or addr not in self.store:
                            raise InteractiveInterpreterException(f"No such element in store: {remainder}")
                        val = self.store.get(addr)
                    print(f"store[{remainder}]: {val}")
                else:
                    print(self.store)
            else:
                # Handle as regular input.
                if self.multiline:
                    self.lines.append(line)
                else:
                    # Handle as single input.
                    lexemes = vl.lex_line(line)
                    parse = GRAMMAR.parse_rule(SINGLE_INPUT_RULE, lexemes)
                    if isinstance(parse, NoParse):
                        lexemes.append(vl.NEWLINE)
                        parse = GRAMMAR.parse_rule(SINGLE_INPUT_RULE, lexemes)
                        if isinstance(parse, NoParse):
                            raise InteractiveInterpreterException(f"Could not parse input: {repr(line)}")
                    result = start_eval(parse.ast, env=self.env, store=self.store)
                    if result.val is not None:
                        # Show the result.
                        print(result.val)
                    self.env = result.env
                    self.store = result.store

    def _update_prompt(self):
        if self.multiline:
            self.prompt = MULTILINE_INPUT_PROMPT
        else:
            self.prompt = SINGLE_INPUT_PROMPT

    def parseline(self, line):
        if self.multiline:
            line = line.rstrip()
        else:
            line = line.strip()
        return None, None, line
