from abc import ABC
from typing import Any, Callable, List


Token = Any
Parse = List[Token]
PartialParse = List[Parse]


class AmbiguousParseError(Exception):
    pass


class AST(ABC):
    pass


SemiAST = List[AST]
RedFunc = Callable[[SemiAST], SemiAST]


class ASTChar(AST):
    def __init__(self, token: Token):
        self.token = token


class ASTPair(AST):
    def __init__(self, left: SemiAST, right: SemiAST):
        self.left = left
        self.right = right


class ASTRep(AST):
    def __init__(self, partial: SemiAST):
        self.parse = partial


class Language(ABC):
    pass


class Empty(Language):
    def __repr__(self):
        return "∅"


class Epsilon(Language):
    def __init__(self, parsed_token: Token):
        self.token = parsed_token

    def __repr__(self):
        return "ε"


class Literal(Language):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)


class RuleLiteral(Language):
    def __init__(self, name: str, grammar):
        self.name = name
        self.grammar = grammar

    @property
    def lang(self) -> Language:
        return self.grammar[self.name]

    def __repr__(self):
        return "<" + self.name + ">"


class Concat(Language):
    def __init__(self, left: Language, right: Language):
        self.left = left
        self.right = right

    def __repr__(self):
        if isinstance(self.right, Epsilon):
            return repr(self.left)
        if self._all_chars():
            return repr(self.left) + repr(self.right)
        else:
            return repr(self.left) + " ◦ " + repr(self.right)

    def _all_chars(self):
        if isinstance(self.left, Literal):
            if isinstance(self.right, Literal):
                return True
            if isinstance(self.right, Concat):
                return self.right._all_chars()
        return False


class Alt(Language):
    def __init__(self, this: Language, that: Language):
        self.this = this
        self.that = that

    def __repr__(self):
        return repr(self.this) + " ∪ " + repr(self.that)


class Rep(Language):
    def __init__(self, lang: Language):
        self.lang = lang

    def __repr__(self):
        return "{" + repr(self.lang) + "}*"


class Red(Language):
    def __init__(self, lang: Language, func: RedFunc):
        self.lang = lang
        self.func = func

    def __repr__(self):
        return "⌊" + repr(self.lang) + " --> f⌋"


def linguify(x) -> Language:
    if not isinstance(x, Language):
        return literal(x)
    return x


def empty():
    return Empty()


def eps(token: Token):
    return Epsilon(token)


def literal(c):
    return Literal(c)


def concat(l1: Language, *ls: Language):
    l1 = linguify(l1)
    if len(ls) == 0:
        return l1
    elif len(ls) == 1:
        l2 = linguify(ls[0])
        if isinstance(l1, Empty) or isinstance(l2, Empty):
            return empty()
        if isinstance(l1, Epsilon):
            # TODO: explain this
            def f(x):
                return [ASTPair(parse_null(l1), x)]
            return red(l2, f)
        if isinstance(l2, Epsilon):
            def f(x):
                return [ASTPair(parse_null(l2), x)]
            return red(l1, f)
        return Concat(l1, l2)
    else:
        return Concat(l1, concat(*ls))


def alt(l1: Language, *ls: Language):
    l1 = linguify(l1)
    if len(ls) == 0:
        return l1
    elif len(ls) == 1:
        l2 = ls[0]
        if isinstance(l1, Empty):
            return l2
        if isinstance(l2, Empty):
            return l1
        return Alt(l1, l2)
    else:
        return Alt(l1, alt(*ls))


def rep(lang: Language):
    return Rep(linguify(lang))


def opt(lang: Language):
    return alt(lang, eps(None))


def red(lang: Language, f: RedFunc):
    return Red(linguify(lang), f)


def is_empty(s: List) -> bool:
    if len(s) == 0:
        return True
    return False


def is_nullable(lang: Language) -> bool:
    if isinstance(lang, Empty):
        return False
    if isinstance(lang, Epsilon):
        return True
    if isinstance(lang, Literal):
        return False
    if isinstance(lang, RuleLiteral):
        return is_nullable(lang.lang)
    if isinstance(lang, Alt):
        return is_nullable(lang.this) or is_nullable(lang.that)
    if isinstance(lang, Concat):
        return is_nullable(lang.left) and is_nullable(lang.right)
    if isinstance(lang, Rep):
        return True


def derive(lang: Language, c) -> Language:
    if isinstance(lang, Empty):
        return empty()
    if isinstance(lang, Epsilon):
        return empty()
    if isinstance(lang, Literal):
        return eps(c) if lang.value == c else empty()
    if isinstance(lang, RuleLiteral):
        return derive(lang.lang, c)  # TODO: Is this the best way to do this?
    if isinstance(lang, Concat):
        if is_nullable(lang.left):
            return alt(concat(derive(lang.left, c), lang.right), derive(lang.right, c))
        else:
            return concat(derive(lang.left, c), lang.right)
    if isinstance(lang, Alt):
        return alt(derive(lang.this, c), derive(lang.that, c))
    if isinstance(lang, Rep):
        return concat(derive(lang.lang, c), lang)
    if isinstance(lang, Red):
        return red(derive(lang.lang, c), lang.func)


def parse(lang: Language, xs):
    from functools import reduce
    return flatten_parse(collapse_parse(parse_null(reduce(derive, xs, lang))))


def parse_null(lang: Language) -> SemiAST:
    if isinstance(lang, Empty):
        return []
    if isinstance(lang, Epsilon):
        if lang.token is None:
            return []
        else:
            return [ASTChar(lang.token)]
    if isinstance(lang, Literal):
        return []
    if isinstance(lang, RuleLiteral):
        return parse_null(lang.lang)
    if isinstance(lang, Concat):
        return [ASTPair(parse_null(lang.left), parse_null(lang.right))]
    if isinstance(lang, Alt):
        return parse_null(lang.this) + parse_null(lang.that)
    if isinstance(lang, Rep):
        return [ASTRep(parse_null(lang.lang))]
    if isinstance(lang, Red):
        return lang.func(parse_null(lang.lang))
    raise ValueError(f"unknown language: {lang}")


def flatten_parse(nodes: SemiAST) -> Parse:
    seq: Parse = []

    def _flatten_parse(ns: SemiAST):
        if len(ns) == 0:
            # Nothing to flatten. Easy.
            return
        elif len(ns) == 1:
            node = ns[0]
            if isinstance(node, ASTChar):
                seq.append(node.token)
            elif isinstance(node, ASTPair):
                _flatten_parse(node.left)
                _flatten_parse(node.right)
            elif isinstance(node, ASTRep):
                _flatten_parse(node.parse)
        else:
            # Cannot flatten; there are too many things!
            raise AmbiguousParseError

    _flatten_parse(nodes)
    return seq


def collapse_parse(nodes: SemiAST) -> SemiAST:
    if is_empty(nodes):
        return nodes
    new_nodes = []
    # Now build a new set, eliminating any empty parses.
    for node in nodes:
        if isinstance(node, ASTChar):
            # Always add terminals.
            new_nodes.append(node)
        elif isinstance(node, ASTPair):
            left = collapse_parse(node.left)
            right = collapse_parse(node.right)
            if not (is_empty(left) or is_empty(right)):
                # Add only if neither part of the sequence is empty.
                new_nodes.append(ASTPair(left, right))
        elif isinstance(node, ASTRep):
            # Always add the ASTRep, even if its interior parse comes up empty.
            # This ensures we can properly parse repeated tokens.
            new_nodes.append(ASTRep(collapse_parse(node.parse)))
    if len(new_nodes) > 1:  # TODO: consider making a toggle
        raise AmbiguousParseError
    return new_nodes


def is_match(w: list, lang: Language) -> bool:
    if not w:
        return is_nullable(lang)
    else:
        return is_match(w[1:], derive(lang, w[0]))


def mkstr(s: str) -> Language:
    return concat(*map(literal, s))


# TODO: check for ambiguities (sets of size != 1)
# TODO: look up Michael's OOPSLA tree automata paper
# TODO: implement printing ASTs like:
#   (char 'a')
#
#   (pair (char 'f')
#         (pair (char 'o')
#               (char 'o')))
# TODO: currently not throwing ambiguitiy errors; try:
#   l1 = cat(char('f'), alt(mkstr('oo'), mkstr('rak')))
#   parse(l1, 'f')
# TODO: rename things as desired
# TODO: convert grammar.py to use this version of the languages instead
