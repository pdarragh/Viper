import re

from re import _pattern_type as PatternType
from typing import List, Union

__all__ = [
    'Indent', 'OpenParen', 'CloseParen', 'Name', 'Class', 'Operator',
    'lex_file', 'lex_line',
]

# FIXME: Ambiguity between names with symbol endings and operators with those same symbols.


# Regular expression patterns.
INDENT_SIZE = 4
RE_LEADING_INDENT = re.compile(fr'^((?: {{{INDENT_SIZE}}})*)(.*)$')

RE_NUMBER = re.compile(r'(?:\d+)'                           # 42
                       r'|'
                       r'(?:\.\d+(?:[eE][+-]?\d+)?)'        # .42 | .42e-8
                       r'|'
                       r'(?:\d[eE][+-]?\d+)'                # 42e3
                       r'|'
                       r'(?:\d+\.\d*(?:[eE][+-]?\d+)?)')    # 42.7e2 | 42.e9 | 42. | 42.3e-8
RE_NAME = re.compile(r'_+|(?:_*[a-z][_a-zA-Z0-9]*(?:-[_a-zA-Z0-9]*)*[!@$%^&*?a-zA-Z0-9]?)')
RE_CLASS = re.compile(r'[A-Z][-_a-zA-Z0-9]*')
RE_OPERATOR = re.compile(r'[!@$%^&*()-=+|/?<>\[\]{}~]+')

RE_PREFIX_OP = re.compile(r'(?P<op>' + RE_OPERATOR.pattern + r')(?P<val>(?:' + RE_NAME.pattern + '|' +
                          RE_CLASS.pattern + '))')
RE_POSTFIX_OP = re.compile(r'(?P<val>(?:' + RE_NAME.pattern + '|' + RE_CLASS.pattern + '))(?P<op>' +
                           RE_OPERATOR.pattern + r')')
RE_OPEN_PAREN = re.compile(r'(?P<left>' + RE_NAME.pattern + ')?\((?P<right>' + RE_NAME.pattern + ')?')
RE_CLOSE_PAREN = re.compile(r'(?P<left>' + RE_NAME.pattern + ')?\)(?P<right>' + RE_NAME.pattern + ')?')
RE_BOTH_PAREN = re.compile(r'(?P<left>' + RE_NAME.pattern + ')?\((?P<inside>' + RE_NAME.pattern + ')?\)(?P<right>' +
                           RE_NAME.pattern + ')?')


# Regular expression magic class for making if/else matching simpler. Idea from:
#   http://code.activestate.com/recipes/456151-using-rematch-research-and-regroup-in-if-elif-elif/
class RegexMatcher:
    def __init__(self, token):
        self._token = token
        self._match = None

    def match(self, pattern: PatternType):
        self._match = pattern.match(self._token)
        return self._match

    def fullmatch(self, pattern: PatternType):
        self._match = pattern.fullmatch(self._token)
        return self._match

    def search(self, pattern: PatternType):
        self._match = pattern.search(self._token)
        return self._match

    def group(self, grp: Union[int, str]):
        return self._match.group(grp)

    def groups(self):
        return self._match.groups()


# Tokens
class Lexeme:
    def __init__(self, text, repl_with_text=True):
        self.text = text
        self._repl_with_text = repl_with_text

    def __repr__(self):
        if self._repl_with_text:
            return f'{type(self).__name__}({self.text})'
        else:
            return type(self).__name__

    def __str__(self):
        return self.text

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.text == other.text

    def __ne__(self, other):
        return not self.__eq__(other)


class Indent(Lexeme):
    def __init__(self):
        super().__init__(' ' * INDENT_SIZE, False)


class NewLine(Lexeme):
    def __init__(self):
        super().__init__('\n', False)


class OpenParen(Lexeme):
    def __init__(self):
        super().__init__('(', False)


class CloseParen(Lexeme):
    def __init__(self):
        super().__init__(')', False)


class Number(Lexeme):
    pass


class Name(Lexeme):
    pass


class Class(Lexeme):
    pass


class Operator(Lexeme):
    pass


INDENT = Indent()
NEWLINE = NewLine()
OPEN_PAREN = OpenParen()
CLOSE_PAREN = CloseParen()


# Lexer errors.
class LexerError(Exception):
    pass


# Lexer implementation.
class Lexer:
    @classmethod
    def lex(cls, text: str) -> List[Lexeme]:
        lexemes = []
        for line in text.splitlines():
            lexemes.extend(cls.lex_line(line))
            lexemes.append(NEWLINE)
        return lexemes

    @classmethod
    def lex_file(cls, file: str) -> List[Lexeme]:
        lexemes = []
        with open(file) as f:
            for line in f:
                lexemes.extend(cls.lex_line(line))
                lexemes.append(NEWLINE)
        return lexemes

    @classmethod
    def lex_line(cls, line: str) -> List[Lexeme]:
        lexemes = []
        if not line:
            return lexemes
        # Remove properly-indented leading whitespace.
        match = RE_LEADING_INDENT.match(line)
        if match is None:
            raise LexerError(f"invalid line given: '{line}'")
        indentation, rest = match.groups()
        for indentation_level in range(len(indentation) // INDENT_SIZE):
            lexemes.append(Indent())
        for token in rest.split():
            for lexeme in cls.lex_token(token):
                lexemes.append(lexeme)
        return lexemes

    @classmethod
    def lex_token(cls, token: str) -> List[Lexeme]:
        matcher = RegexMatcher(token)
        lexemes = []
        if matcher.fullmatch(RE_NUMBER):
            lexemes.append(Number(matcher.group(0)))
        elif matcher.fullmatch(RE_NAME):
            lexemes.append(Name(matcher.group(0)))
        elif matcher.fullmatch(RE_CLASS):
            lexemes.append(Class(matcher.group(0)))
        elif matcher.fullmatch(RE_OPERATOR):
            lexemes.append(Operator(matcher.group(0)))
        elif matcher.fullmatch(RE_PREFIX_OP):
            lexemes.append(Operator(matcher.group('op')))
            lexemes.extend(cls.lex_token(matcher.group('val')))
        elif matcher.fullmatch(RE_POSTFIX_OP):
            lexemes.extend(cls.lex_token(matcher.group('val')))
            lexemes.append(Operator(matcher.group('op')))
        elif matcher.fullmatch(RE_OPEN_PAREN):
            lexemes.extend(cls.lex_token(matcher.group('left')))
            lexemes.append(OPEN_PAREN)
            lexemes.extend(cls.lex_token(matcher.group('right')))
        elif matcher.fullmatch(RE_CLOSE_PAREN):
            lexemes.extend(cls.lex_token(matcher.group('left')))
            lexemes.append(CLOSE_PAREN)
            lexemes.extend(cls.lex_token(matcher.group('right')))
        elif matcher.fullmatch(RE_BOTH_PAREN):
            lexemes.extend(cls.lex_token(matcher.group('left')))
            lexemes.append(OPEN_PAREN)
            lexemes.extend(cls.lex_token(matcher.group('inside')))
            lexemes.append(CLOSE_PAREN)
            lexemes.extend(cls.lex_token(matcher.group('right')))
        else:
            raise LexerError(f"invalid token: '{token}'")
        return lexemes


lex_file = Lexer.lex_file
lex_line = Lexer.lex_line
