from typing import ClassVar


class GrammarToken:
    def __init__(self, lexeme_class: ClassVar, text=None):
        self._lexeme_class = lexeme_class
        self._text = text

    def __eq__(self, other):
        if isinstance(other, GrammarToken):
            return self._lexeme_class == other._lexeme_class
        return isinstance(other, self._lexeme_class)

    def __str__(self):
        if self._text is not None:
            return self._text
        else:
            return f'{self._lexeme_class.__name__}Token'

    def __repr__(self):
        return str(self)
