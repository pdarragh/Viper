import re

from typing import List


# Regular expression patterns.
INDENT_SIZE = 4
RE_LEADING_INDENT = re.compile(fr'^((?: {{{INDENT_SIZE}}})*)(.*)$')
RE_NAME = re.compile(fr'[a-zA-Z0-9_]+(?:-[a-zA-Z0-9_]+)*[!?]?')


# Tokens
class Lexeme:
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return type(self).__name__

    def __str__(self):
        return self.text


class INDENT(Lexeme):
    def __init__(self):
        super().__init__(' ' * INDENT_SIZE)


class NAME(Lexeme):
    pass


# Lexer errors.
class LexerError(Exception):
    pass


class Lexer:
    @classmethod
    def lex(cls, text: str) -> List[Lexeme]:
        lexemes = []
        for line in text.splitlines():
            lexemes.extend(cls.lex_line(line))
        return lexemes

    @classmethod
    def lex_line(cls, line: str) -> List[Lexeme]:
        lexemes = []
        # Remove properly-indented leading whitespace.
        match = RE_LEADING_INDENT.match(line)
        if match is None:
            raise LexerError(f"invalid line given: '{line}'")
        indentation, rest = match.groups()
        for indentation_level in range(len(indentation) // INDENT_SIZE):
            lexemes.append(INDENT())
        for token in rest.split():
            lexeme = cls.lex_token(token)
            lexemes.append(lexeme)
        return lexemes

    @classmethod
    def lex_token(cls, token: str) -> Lexeme:
        if RE_NAME.fullmatch(token):
            return NAME(token)
        else:
            raise LexerError(f"invalid token: '{token}'")
