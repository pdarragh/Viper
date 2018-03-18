from viper.lexer.lexemes import *

import re

from re import _pattern_type as PatternType
from typing import List, Union

__all__ = [
    'LexerError', 'Lexer', 'lex_file', 'lex_lines', 'lex_line',
]

# FIXME: Ambiguity between names with symbol endings and operators with those same symbols.
# FIXME: Ambiguity between function call and postfix Operator `()`
# TODO: Handle strings.
# TODO: Determine whether parentheses should be special or should be considered individual operators.
# TODO: Investigate using built-in regex magic parser:
#         http://code.activestate.com/recipes/457664-hidden-scanner-functionality-in-re-module/


# Regular expression patterns.
RE_LEADING_INDENT = re.compile(fr'^((?: {{{INDENT_SIZE}}})*)(.*)$')

RE_COMMA = re.compile(r',')
RE_NUMBER = re.compile(r'(?:\d+)'                           # 42
                       r'|'
                       r'(?:\.\d+(?:[eE][+-]?\d+)?)'        # .42 | .42e-8
                       r'|'
                       r'(?:\d+[eE][+-]?\d+)'               # 42e3
                       r'|'
                       r'(?:\d+\.\d*(?:[eE][+-]?\d+)?)')    # 42.7e2 | 42.e9 | 42. | 42.3e-8
RE_NAME = re.compile(r'_+|(?:_*[a-z][_a-zA-Z0-9]*(?:-[_a-zA-Z0-9]+)*[!@$%^&*?]?)')
RE_CLASS = re.compile(r'[A-Z][_a-zA-Z0-9]*(?:-[_a-zA-Z0-9]+)*')
RE_PARENS = re.compile(r'\(\)')
RE_OPERATOR = re.compile(r'[!@$%^&*()\-=+|:/?<>\[\]{}~.]+')


def make_infix_re(pattern: PatternType, group_name: str) -> PatternType:
    return re.compile(r'(?P<left_val>.*)(?P<' + group_name + '>' + pattern + r')(?P<right_val>.*)')


RE_INFIX_COMMA = make_infix_re(RE_COMMA.pattern, 'comma')
RE_INFIX_OP = make_infix_re(RE_OPERATOR.pattern, 'op')


# Regular expression magic class for making if/else matching simpler. Idea from:
#   http://code.activestate.com/recipes/456151-using-rematch-research-and-regroup-in-if-elif-elif/
class RegexMatcher:
    def __init__(self, token):
        self._token = token
        self._match = None

    def fullmatch(self, pattern: PatternType):
        self._match = pattern.fullmatch(self._token)
        return self._match

    def group(self, grp: Union[int, str]):
        return self._match.group(grp)


# Lexer errors.
class LexerError(Exception):
    pass


# Lexer implementation.
class Lexer:
    @classmethod
    def lex_file(cls, file: str) -> List[Lexeme]:
        with open(file) as f:
            text = f.read()
        return lex_lines(text)

    @classmethod
    def lex_lines(cls, text: str) -> List[Lexeme]:
        lexed_lines = []
        prev_indents = 0
        lines = text.splitlines()
        for i in range(len(lines)):
            line = lines[i]
            lexed_line = cls.lex_line(line)
            if i != 0:
                # If this isn't the first line, prepend a NEWLINE.
                lexed_line.insert(0, NEWLINE)
            # Append a DEDENT to the previous line for each INDENT missing in this line.
            curr_indents = sum(map(lambda l: isinstance(l, Indent), lexed_line))
            for _ in range(prev_indents - curr_indents):
                lexed_lines[i - 1].append(DEDENT)
            prev_indents = curr_indents
            if i == len(lines) - 1:
                # If this is the last line, append remaining necessary DEDENT tokens.
                for _ in range(prev_indents):
                    lexed_line.append(DEDENT)
                # Also add a NEWLINE and the end-of-file marker.
                lexed_line.append(NEWLINE)
                lexed_line.append(ENDMARKER)
            lexed_lines.append(lexed_line)
        # Flatten the list.
        return [lexeme for lexed_line in lexed_lines for lexeme in lexed_line]

    @classmethod
    def lex_line(cls, line: str) -> List[Lexeme]:
        lexemes = []
        if not line:
            return lexemes
        # Remove properly-indented leading whitespace.
        match = RE_LEADING_INDENT.match(line)
        if match is None:  # pragma: no cover
            raise LexerError(f"invalid line given: '{line}'")
        indentation, rest = match.groups()
        for indentation_level in range(len(indentation) // INDENT_SIZE):
            lexemes.append(INDENT)
        for token in rest.split():
            for lexeme in cls.lex_token(token):
                lexemes.append(lexeme)
        return lexemes

    @classmethod
    def lex_token(cls, token: str) -> List[Lexeme]:
        matcher = RegexMatcher(token)
        lexemes = []
        if not token:
            return lexemes
        elif matcher.fullmatch(RE_COMMA):
            lexemes.append(COMMA)
        elif matcher.fullmatch(RE_NUMBER):
            lexemes.append(Number(matcher.group(0)))
        elif matcher.fullmatch(RE_NAME):
            lexemes.append(Name(matcher.group(0)))
        elif matcher.fullmatch(RE_CLASS):
            lexemes.append(Class(matcher.group(0)))
        elif matcher.fullmatch(RE_PARENS):
            lexemes.append(OPEN_PAREN)
            lexemes.append(CLOSE_PAREN)
        elif matcher.fullmatch(RE_OPERATOR):
            symbol = matcher.group(0)
            if symbol == PERIOD.text:
                lexemes.append(PERIOD)
            elif symbol == OPEN_PAREN.text:
                lexemes.append(OPEN_PAREN)
            elif symbol == CLOSE_PAREN.text:
                lexemes.append(CLOSE_PAREN)
            elif symbol == COLON.text:
                lexemes.append(COLON)
            elif symbol == ARROW.text:
                lexemes.append(ARROW)
            else:
                lexemes.append(Operator(symbol))
        elif matcher.fullmatch(RE_INFIX_COMMA):
            lexemes.extend(cls.lex_token(matcher.group('left_val')))
            lexemes.append(COMMA)
            lexemes.extend(cls.lex_token(matcher.group('right_val')))
        elif matcher.fullmatch(RE_INFIX_OP):
            lexemes.extend(cls.lex_token(matcher.group('left_val')))
            lexemes.extend(cls.lex_token(matcher.group('op')))
            lexemes.extend(cls.lex_token(matcher.group('right_val')))
        else:
            raise LexerError(f"invalid token: '{token}'")
        return lexemes


lex_file = Lexer.lex_file
lex_lines = Lexer.lex_lines
lex_line = Lexer.lex_line
