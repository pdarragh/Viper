import viper.lexer as vl

from viper.parser import *
from viper.interpreter.interpreter import *

import cmd


SINGLE_INPUT_RULE = 'single_input'
MULTILINE_INPUT_RULE = 'file_input'


class InteractiveInterpreterException(Exception):
    def __init__(self, output: str):
        self.output = output


class InteractiveInterpreter(cmd.Cmd):  # pragma: no cover
    prompt = '>>> '

    def __init__(self):
        super().__init__()
        self.multiline = False
        self.env = None
        self.store = None

    def default(self, line: str):
        line.replace('\\', '\\\\')
        if line == ':{':
            if self.multiline:
                raise InteractiveInterpreterException(f"Already in multiline mode.")
            else:
                # Begin multi-line processing.
                self.multiline = True
        elif line == ':}':
            if self.multiline:
                # End multi-line processing.
                self.multiline = False
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
                        raise InteractiveInterpreterException(f"No such element in store: {remainder}")
                    else:
                        print(f"store[{remainder}]: {val}")
                else:
                    print(self.store)
            else:
                # Handle as regular input.
                if self.multiline:
                    # TODO: Implement this.
                    raise InteractiveInterpreterException(f"Multiline input not supported at this time.")
                else:
                    # Handle as single input.
                    lexemes = vl.lex_line(line)
                    parse = GRAMMAR.parse_rule(SINGLE_INPUT_RULE, lexemes)
                    if isinstance(parse, NoParse):
                        lexemes.append(vl.NEWLINE)
                        parse = GRAMMAR.parse_rule(SINGLE_INPUT_RULE, lexemes)
                        if isinstance(parse, NoParse):
                            raise InteractiveInterpreterException(f"Could not parse input: {line}")
                    result = start_eval(parse.ast, env=self.env, store=self.store)
                    if result.val is not None:
                        # Show the result.
                        print(result.val)
                    self.env = result.env
                    self.store = result.store
