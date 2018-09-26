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

ALL_MODES = LexMode | ParseMode | EvalMode | ExecMode

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
        self.envs = None
        self.store = None
        self.handle_exceptions = True

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
                if self.handle_exceptions:
                    self._handle_error(f"{type(e).__name__}: {str(e)}")
                else:
                    raise e

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
                # Interpret the result.
                self._handle_input('\n'.join(self.lines))
                # End multi-line processing.
                self.multiline = False
                self.lines = []
                self._update_prompt()
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
                    val = self.envs.get(remainder)
                    if val is None:
                        raise InteractiveInterpreterException(f"No such element in environment: {remainder}")
                    else:
                        print(f"env[{remainder}]: {val}")
                else:
                    print(self.envs)
            elif starter in {':s', ':store'}:
                # Get information from the current store.
                if remainder:
                    val = self.store.get(remainder)
                    if val is None:
                        try:
                            addr = int(remainder)
                        except ValueError:
                            addr = self.envs.get(remainder)
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
                self._handle_input(remainder, LexMode)
            elif starter in {':p', ':parse'}:
                # Print the AST of the parsed remainder.
                if not remainder:
                    raise InteractiveInterpreterException(f"Missing argument for AST construction.")
                self._handle_input(remainder, ParseMode)
            elif starter in {':set'}:
                if not remainder:
                    raise InteractiveInterpreterException(f"No argument given for :set command.")
                split_subcmd = remainder.split(maxsplit=1)
                subcmd = split_subcmd[0]
                if len(split_subcmd) == 2:
                    remainder = split_subcmd[1]
                else:
                    remainder = None
                if subcmd == 'mode':
                    if remainder is None:
                        # Show current mode.
                        print(f":set mode: {bin(self.mode)[2:].zfill(4)}")
                    else:
                        self.mode = self._parse_mode(remainder)
                elif subcmd == 'exceptions':
                    if remainder is None:
                        print(f":set exceptions: {'on' if self.handle_exceptions else 'off'}")
                    else:
                        if remainder == 'on':
                            self.handle_exceptions = True
                        elif remainder == 'off':
                            self.handle_exceptions = False
                        else:
                            raise InteractiveInterpreterException(f"Unsupported value for :set exceptions: {remainder}")
                else:
                    raise InteractiveInterpreterException(f"Unsupported :set subcommand given: {subcmd}")
            else:
                # Handle as regular input.
                if self.multiline:
                    self.lines.append(line)
                else:
                    # Handle as single input.
                    self._handle_input(line)

    def _handle_input(self, text: str, mode: InterpreterMode=None):
        if mode is None:
            mode = self.mode

        lexemes = self._lex_text(text)
        if mode & LexMode:
            print(lexemes)
            if mode <= LexMode:
                return

        parse = self._parse_lexemes(lexemes)
        if isinstance(parse, NoParse):
            raise InteractiveInterpreterException(f"Could not parse input: {repr(text)}")
        assert isinstance(parse, SingleParse)
        ast = parse.ast
        if mode & ParseMode:
            print(ast_to_string(ast))
            if mode <= ParseMode:
                return

        result = start_eval(ast, envs=self.envs, store=self.store)
        if mode & EvalMode:
            if result.val is not None:
                # Show the result if it's not the unit type.
                if not isinstance(result.val, UnitVal):
                    print(result.val)
            if mode <= EvalMode:
                return

        if mode & ExecMode:
            self.envs = result.envs
            self.store = result.store

    def _lex_text(self, text: str) -> List[vl.Lexeme]:
        if self.multiline:
            return [vl.NEWLINE, vl.INDENT] + vl.lex_lines(text)[:-1] + [vl.DEDENT]
        else:
            return vl.lex_line(text)

    def _parse_lexemes(self, lexemes: List[vl.Lexeme]) -> Parse:
        if self.multiline:
            return GRAMMAR.parse_rule(MULTILINE_INPUT_RULE, lexemes)
        else:
            parse = GRAMMAR.parse_rule(SINGLE_INPUT_RULE, lexemes)
            if isinstance(parse, NoParse):
                parse = GRAMMAR.parse_rule(SINGLE_INPUT_RULE, lexemes + [vl.NEWLINE])
            return parse

    def _parse_mode(self, text: str) -> int:
        parts = text.split()
        mode = self.mode
        for part in parts:
            if part.startswith('+'):
                for switch in list(part)[1:]:
                    mode |= self._parse_switch(switch)
            elif part.startswith('-'):
                for switch in list(part)[1:]:
                    mode &= (ALL_MODES & ~self._parse_switch(switch))
            else:
                try:
                    val = int(part, base=2)
                except ValueError:
                    raise InteractiveInterpreterException(f"Invalid mode value: {part}")
                if val < 0 or val > ALL_MODES:
                    raise InteractiveInterpreterException(f"Mode value outside valid range: {val}")
                mode = val
        return mode

    def _parse_switch(self, c: str) -> int:
        if c == 'l':
            return LexMode
        elif c == 'p':
            return ParseMode
        elif c == 'e':
            return EvalMode
        elif c == 'x':
            return ExecMode
        elif c == 'a':
            return ALL_MODES
        else:
            raise InteractiveInterpreterException(f"Invalid mode switch specification: {c}")

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
