import viper.lexer as vl

from viper.parser import *
from viper.interpreter.interpreter import *

import cmd


SINGLE_INPUT_RULE = 'single_input'
MULTILINE_INPUT_RULE = 'stmt_block'

SINGLE_INPUT_PROMPT = '>>> '
MULTILINE_INPUT_PROMPT = '... '

LexMode = 1 << 0
ParseMode = 1 << 1
EvalMode = 1 << 2
ExecMode = 1 << 3

InterpreterMode = int


class InteractiveInterpreterException(Exception):
    def __init__(self, output: str):
        self.output = output


class InteractiveInterpreter(cmd.Cmd):  # pragma: no cover
    prompt = SINGLE_INPUT_PROMPT

    def __init__(self):
        super().__init__(completekey=None)
        self.mode: InterpreterMode = EvalMode | ExecMode
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
            except EOFError:
                print()
                cont = False
            except Exception as e:
                self._handle_error(f"{type(e).__name__}: {str(e)}")

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
        line = line.replace('\\', '\\\\').replace('\t', '    ')
        if line == 'EOF':
            raise EOFError
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
                self._handle_lines(self.lines)
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
                    print(f"store[{remainder}]: {repr(val)}")
                else:
                    print(self.store)
            elif starter in {':l', ':lex'}:
                # Print the lexemes of the lexed remainder.
                if not remainder:
                    raise InteractiveInterpreterException(f"Missing argument for lexeme construction.")
                self._handle_line(remainder, LexMode)
            elif starter in {':a', ':ast'}:
                # Print the AST of the parsed remainder.
                if not remainder:
                    raise InteractiveInterpreterException(f"Missing argument for AST construction.")
                self._handle_line(remainder, ParseMode)
            else:
                # Handle as regular input.
                if self.multiline:
                    self.lines.append(line)
                else:
                    # Handle as single input.
                    self._handle_line(line)

    def _handle_line(self, line: str, mode: InterpreterMode=None):
        if mode is None:
            mode = self.mode

        lexemes = vl.lex_line(line)
        if mode & LexMode:
            print(lexemes)
            if mode <= LexMode:
                return

        parse = GRAMMAR.parse_rule(SINGLE_INPUT_RULE, lexemes)
        if isinstance(parse, NoParse):
            lexemes.append(vl.NEWLINE)
            parse = GRAMMAR.parse_rule(SINGLE_INPUT_RULE, lexemes)
            if isinstance(parse, NoParse):
                raise InteractiveInterpreterException(f"Could not parse input: {repr(line)}")
        if mode & ParseMode:
            print(ast_to_string(parse.ast))
            if mode <= ParseMode:
                return

        result = start_eval(parse.ast, env=self.env, store=self.store)
        if mode & EvalMode:
            if result.val is not None:
                # Show the result.
                print(result.val)
            if mode <= EvalMode:
                return

        if mode & ExecMode:
            self.env = result.env
            self.store = result.store

    def _handle_lines(self, lines: List[str], mode: InterpreterMode=None):
        if mode is None:
            mode = self.mode

        lines = '\n'.join(lines)
        lexemes = [vl.NEWLINE, vl.INDENT] + vl.lex_lines(lines)[:-1] + [vl.DEDENT]
        if mode & LexMode:
            print(lexemes)
            if mode <= LexMode:
                return

        parse = GRAMMAR.parse_rule(MULTILINE_INPUT_RULE, lexemes)
        if isinstance(parse, NoParse):
            raise InteractiveInterpreterException(f"Could not parse multiline input: {repr(lines)}")
        if mode & ParseMode:
            print(ast_to_string(parse.ast))
            if mode <= ParseMode:
                return

        result = start_eval(parse.ast, env=self.env, store=self.store)
        if mode <= EvalMode:
            return

        if mode & ExecMode:
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
