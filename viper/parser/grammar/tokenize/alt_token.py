class AltToken:
    def __init__(self, text: str):
        self.text = text

    def __repr__(self):
        return self.text

    def __str__(self):
        return repr(self)


class LiteralToken(AltToken):
    def __repr__(self):
        return '\'' + self.text + '\''


class SpecialToken(AltToken):
    pass


class RepeatToken(AltToken):
    pass


class OptionalToken(AltToken):
    pass


class ParameterExpansionToken(AltToken):
    pass


class SpecialParameterExpansionToken(AltToken):
    pass


class ColonToken(AltToken):
    pass


class BracedToken(AltToken):
    def __init__(self, left: str, right: str):
        self.left = left
        self.right = right
        super().__init__(left + ", " + right)

    def __repr__(self):
        return '{' + self.text + '}'


class RuleToken(AltToken):
    def __repr__(self):
        return '<' + self.text + '>'


class CapitalWordToken(AltToken):
    pass


class ParameterNameToken(AltToken):
    pass
