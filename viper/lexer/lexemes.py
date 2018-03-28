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
        # This is inverted from the standard style because we want for Lexemes to be compared less restrictively.
        # The [Python reference](https://docs.python.org/3/reference/datamodel.html#object.__eq__) states:
        #
        #   There are no swapped-argument versions of these methods (to be used
        #   when the left argument does not support the operation but the right
        #   argument does). [...] If the operands are of different types, and
        #   right operand’s type is a direct or indirect subclass of the left
        #   operand’s type, the reflected method of the right operand has
        #   priority, otherwise the left operand’s method has priority.
        #
        # This equality method is used primarily for comparing lexed inputs with expected grammar productions.
        # (Specifically, see the `derive' method in viper.parser.languages.) To avoid a hacked-together specialty Lexeme
        # class purely for such comparisons, I opted to invert the type-checking in this method. (Note also that
        # subclassing is considered — the classes need not be identical.)
        if not isinstance(self, type(other)):
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


class EndMarker(Lexeme):
    def __init__(self):
        super().__init__('EOF', False)


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


class Ellipsis(Lexeme):
    def __init__(self):
        super().__init__('...', False)


class Number(Lexeme):
    pass


class Name(Lexeme):
    pass


class ReservedName(Lexeme):
    pass


class Class(Lexeme):
    pass


class ReservedClass(Lexeme):
    pass


class Operator(Lexeme):
    pass


INDENT = Indent()
DEDENT = Dedent()
ENDMARKER = EndMarker()
NEWLINE = NewLine()
PERIOD = Period()
COMMA = Comma()
OPEN_PAREN = OpenParen()
CLOSE_PAREN = CloseParen()
COLON = Colon()
ARROW = Arrow()
ELLIPSIS = Ellipsis()
