INDENT_SIZE = 4


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

    def __hash__(self):
        return hash(self.text)


class Indent(Lexeme):
    def __init__(self):
        super().__init__(' ' * INDENT_SIZE, False)


class Dedent(Lexeme):
    def __init__(self):
        super().__init__('', False)


class NewLine(Lexeme):
    def __init__(self):
        super().__init__('\n', False)


class Period(Lexeme):
    def __init__(self):
        super().__init__('.', False)


class Comma(Lexeme):
    def __init__(self):
        super().__init__(',', False)


class OpenParen(Lexeme):
    def __init__(self):
        super().__init__('(', False)


class CloseParen(Lexeme):
    def __init__(self):
        super().__init__(')', False)


class Colon(Lexeme):
    def __init__(self):
        super().__init__(':', False)


class Arrow(Lexeme):
    def __init__(self):
        super().__init__('->', False)


class Number(Lexeme):
    pass


class Keyword(Lexeme):
    pass


class Name(Lexeme):
    pass


class Class(Lexeme):
    pass


class Operator(Lexeme):
    pass


INDENT = Indent()
DEDENT = Dedent()
NEWLINE = NewLine()
PERIOD = Period()
COMMA = Comma()
OPEN_PAREN = OpenParen()
CLOSE_PAREN = CloseParen()
COLON = Colon()
ARROW = Arrow()
