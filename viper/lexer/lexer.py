from .reserved_tokens import *
from viper.error import ViperError
from viper.lexer.lexemes import *

import re

from typing import List, Match, Pattern, Union

__all__ = [
    'LexerError', 'lex_file', 'lex_lines', 'lex_line', 'lex_token',
]

# FIXME: Ambiguity between names with symbol endings and operators with those same symbols.
# TODO: Investigate using built-in regex magic parser:
#         http://code.activestate.com/recipes/457664-hidden-scanner-functionality-in-re-module/


# Regular expression patterns.
RE_LEADING_INDENT = re.compile(fr'^((?: {{{INDENT_SIZE}}})*)(.*)$')

RE_COMMA = re.compile(r',')
RE_FLOAT = re.compile(r'(?:-?\.\d+(?:[eE][+-]?\d+)?)'       # (-).42 | (-).42e-8
                      r'|'
                      r'(?:-?\d+[eE][+-]?\d+)'              # (-)42e3
                      r'|'
                      r'(?:-?\d+\.\d*(?:[eE][+-]?\d+)?)')   # (-)42.7e2 | (-)42.e9 | (-)42. | (-)42.3e-8
RE_INT = re.compile(r'(?:-?\d+)')                           # (-)42
RE_STRING = re.compile(r'(?<!\\)\"((?:[^\"]|\\\")*)(?!\\)\"')
RE_NAME = re.compile(r'(?:_*[a-z][_a-zA-Z0-9]*(?:-[_a-zA-Z0-9]+)*[!@$%^&*?]?)')
RE_UNDERSCORE = re.compile(r'_+')
RE_CLASS = re.compile(r'[A-Z][_a-zA-Z0-9]*(?:-[_a-zA-Z0-9]+)*')
RE_OPEN_PAREN = re.compile(r'\(')
RE_CLOSE_PAREN = re.compile(r'\)')
RE_OPERATOR = re.compile(r'[!@$%^&*()\-=+|:/?<>\[\]{}~.]+')
RE_WHITESPACE = re.compile(r'\s+')


def make_infix_re(pattern: Pattern, group_name: str) -> Pattern:
    return re.compile(r'(?P<left_val>.*)(?P<' + group_name + '>' + pattern.pattern + r')(?P<right_val>.*)')


RE_INFIX_COMMA = make_infix_re(RE_COMMA, 'comma')
RE_INFIX_OP = make_infix_re(RE_OPERATOR, 'op')


# Regular expression magic class for making if/else matching simpler. Idea from:
#   http://code.activestate.com/recipes/456151-using-rematch-research-and-regroup-in-if-elif-elif/
class LineRegexMatcher:
    def __init__(self, line: str):
        self._line = line
        self._match = None

    def match(self, pattern: Pattern) -> Match:
        self._match = pattern.match(self._line)
        return self._match

    def end(self) -> int:
        return self._match.end()

    def group(self, grp: Union[int, str]) -> str:
        return self._match.group(grp)

    def __next__(self):
        self._line = self._line[self.end():]

    def __bool__(self) -> bool:
        return bool(self._line)


class LexerError(ViperError):
    pass


def lex_file(file: str) -> List[Lexeme]:
    with open(file) as f:
        text = f.read()
    return lex_lines(text)


def lex_lines(text: str) -> List[Lexeme]:
    all_lexemes: List[Lexeme] = []
    prev_indents = 0
    lines = text.splitlines()
    for i, line in enumerate(lines):
        # Find the raw number of indentation levels for this line.
        indent_match = RE_LEADING_INDENT.match(line)
        if indent_match is None:  # pragma: no cover
            raise LexerError(f"invalid line indentation given: '{line}'")
        indentation, rest = indent_match.groups()
        rest = rest.strip()
        if not rest:
            # Don't use blank lines to handle indentation.
            continue
        if rest.startswith('#'):
            # Skip comments.
            continue
        lexemes = lex_line(rest)
        curr_indents = len(indentation) // INDENT_SIZE
        # Determine whether we need to add indents, dedents, or neither.
        indent_diff = curr_indents - prev_indents
        prev_indents = curr_indents
        if indent_diff > 0:
            # This line is more indented than the previous line.
            for _ in range(indent_diff):
                lexemes.insert(0, INDENT)
            # Add a newline before all the indents.
            lexemes.insert(0, NEWLINE)
        elif indent_diff < 0:
            # This line is less indented than the previous line, which means DEDENT tokens are needed.
            for _ in range(abs(indent_diff)):
                lexemes.insert(0, DEDENT)
            # Add a newline before the dedents.
            lexemes.insert(0, NEWLINE)
        else:
            # We're at the same indentation level, so add neither.
            lexemes.insert(0, NEWLINE)
        # If this is the first line, remove the extraneous NEWLINE.
        if i == 0:
            del(lexemes[0])
        # Add these lexemes to the list.
        all_lexemes += lexemes
    # At the end of the file, append necessary dedents, newline, and end-of-file tokens.
    all_lexemes.append(NEWLINE)
    for _ in range(prev_indents):
        all_lexemes.append(DEDENT)
    all_lexemes.append(ENDMARKER)
    return all_lexemes


def lex_line(line: str) -> List[Lexeme]:
    lexemes = []
    if not line:
        return lexemes
    matcher = LineRegexMatcher(line)
    while matcher:
        if matcher.match(RE_WHITESPACE):
            pass
        elif matcher.match(RE_COMMA):
            lexemes.append(COMMA)
        elif matcher.match(RE_OPEN_PAREN):
            lexemes.append(OPEN_PAREN)
        elif matcher.match(RE_CLOSE_PAREN):
            lexemes.append(CLOSE_PAREN)
        elif matcher.match(RE_FLOAT):
            lexemes.append(Float(matcher.group(0)))
        elif matcher.match(RE_INT):
            lexemes.append(Int(matcher.group(0)))
        elif matcher.match(RE_STRING):
            lexemes.append(String(matcher.group(1)))
        elif matcher.match(RE_NAME):
            text = matcher.group(0)
            if text in RESERVED_NAMES:
                lexemes.append(ReservedName(text))
            else:
                lexemes.append(Name(text))
        elif matcher.match(RE_UNDERSCORE):
            text = matcher.group(0)
            lexemes.append(Underscore(text))
        elif matcher.match(RE_CLASS):
            text = matcher.group(0)
            if text in RESERVED_CLASSES:
                lexemes.append(ReservedClass(text))
            else:
                lexemes.append(Class(text))
        elif matcher.match(RE_OPERATOR):
            symbol = matcher.group(0)
            if symbol == PERIOD.text:
                lexemes.append(PERIOD)
            elif symbol == EQUALS.text:
                lexemes.append(EQUALS)
            elif symbol == OPEN_PAREN.text:
                lexemes.append(OPEN_PAREN)
            elif symbol == CLOSE_PAREN.text:
                lexemes.append(CLOSE_PAREN)
            elif symbol == COLON.text:
                lexemes.append(COLON)
            elif symbol == L_ARROW.text:
                lexemes.append(L_ARROW)
            elif symbol == R_ARROW.text:
                lexemes.append(R_ARROW)
            elif symbol == ELLIPSIS.text:
                lexemes.append(ELLIPSIS)
            else:
                lexemes.append(Operator(symbol))
        elif matcher.match(RE_INFIX_COMMA):
            lexemes.extend(lex_line(matcher.group('left_val')))
            lexemes.append(COMMA)
            lexemes.extend(lex_line(matcher.group('right_val')))
        elif matcher.match(RE_INFIX_OP):
            lexemes.extend(lex_line(matcher.group('left_val')))
            lexemes.extend(lex_line(matcher.group('op')))
            lexemes.extend(lex_line(matcher.group('right_val')))
        else:
            raise LexerError(f"invalid line: '{line}'")
        # Iterate the matcher forward.
        next(matcher)
    return lexemes


def lex_token(token: str) -> List[Lexeme]:
    return lex_line(token)
