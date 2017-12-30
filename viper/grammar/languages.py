from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Callable, List


Token = Any
Parse = List[Token]
PartialParse = List[Parse]


class AmbiguousParseError(Exception):
    pass


class AST(ABC):
    pass


SPPF = List[AST]  # Semi-Packed Parse Forest
RedFunc = Callable[[SPPF], SPPF]
EpsFunc = Callable[[], SPPF]


class ASTChar(AST):
    def __init__(self, token: Token):
        self.token = token


class ASTPair(AST):
    def __init__(self, left: SPPF, right: SPPF):
        self.left = left
        self.right = right


class ASTRep(AST):
    def __init__(self, partial: SPPF):
        self.parse = partial


class Language(ABC):
    def __hash__(self):
        return hash(repr(self))


class Empty(Language):
    def __repr__(self):
        return "∅"

    def __eq__(self, other):
        return isinstance(other, Empty)

    def __hash__(self):
        return super().__hash__()


class Epsilon(Language):
    def __init__(self, func: EpsFunc):
        self.func = func

    def __repr__(self):
        return "ε"

    def __eq__(self, other):
        return other is self

    def __hash__(self):
        return super().__hash__()


class Literal(Language):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)

    def __eq__(self, other):
        if not isinstance(other, Literal):
            return False
        return other.value == self.value

    def __hash__(self):
        return super().__hash__()


class RuleLiteral(Language):
    def __init__(self, name: str, grammar):
        self.name = name
        self.grammar = grammar

    @property
    def lang(self) -> Language:
        return self.grammar[self.name]

    def __repr__(self):
        return "<" + self.name + ">"

    def __eq__(self, other):
        if not isinstance(other, RuleLiteral):
            return False
        return other.name == self.name

    def __hash__(self):
        return super().__hash__()


class DelayRule(Language):
    def __init__(self, rule: RuleLiteral, c):
        self.lang = rule
        self.c = c
        self._derivative = None

    @property
    def derivative(self) -> Language:
        if self._derivative is None:
            self._derivative = derive(self.lang.lang, self.c)
        return self._derivative

    @property
    def is_null(self) -> bool:
        return self._derivative is None

    def __repr__(self):
        return "@D[" + repr(self.c) + "](" + repr(self.lang) + ")"

    def __eq__(self, other):
        if not isinstance(other, DelayRule):
            return False
        return other.lang == self.lang and other.c == self.c

    def __hash__(self):
        return super().__hash__()


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
            return "{" + repr(self.left) + " ◦ " + repr(self.right) + "}"

    def _all_chars(self):
        if isinstance(self.left, Literal):
            if isinstance(self.right, Literal):
                return True
            if isinstance(self.right, Concat):
                return self.right._all_chars()
        return False

    def __eq__(self, other):
        if not isinstance(other, Concat):
            return False
        return other.left == self.left and other.right == self.right

    def __hash__(self):
        return super().__hash__()


class Alt(Language):
    def __init__(self, this: Language, that: Language):
        self.this = this
        self.that = that

    def __repr__(self):
        return "{" + repr(self.this) + " ∪ " + repr(self.that) + "}"

    def __eq__(self, other):
        if not isinstance(other, Alt):
            return False
        return other.this == self.this and other.that == self.that

    def __hash__(self):
        return super().__hash__()


class Rep(Language):
    def __init__(self, lang: Language):
        self.lang = lang

    def __repr__(self):
        return "{" + repr(self.lang) + "}*"

    def __eq__(self, other):
        if not isinstance(other, Rep):
            return False
        return other.lang == self.lang

    def __hash__(self):
        return super().__hash__()


class Red(Language):
    def __init__(self, lang: Language, func: RedFunc):
        self.lang = lang
        self.func = func

    def __repr__(self):
        return "⌊" + repr(self.lang) + " --> f⌋"

    def __eq__(self, other):
        if not isinstance(other, Red):
            return False
        return other.lang == self.lang and other.func == self.func

    def __hash__(self):
        return super().__hash__()


def linguify(x) -> Language:
    if not isinstance(x, Language):
        return literal(x)
    return x


def empty():
    return Empty()


def eps(func: EpsFunc):
    return Epsilon(func)


def literal(c):
    return Literal(c)


def delay(rl: RuleLiteral, c):
    return DelayRule(rl, c)


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
    return alt(lang, eps(lambda: []))


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
    if isinstance(lang, DelayRule):
        return is_nullable(lang.derivative)
    if isinstance(lang, Alt):
        return is_nullable(lang.this) or is_nullable(lang.that)
    if isinstance(lang, Concat):
        return is_nullable(lang.left) and is_nullable(lang.right)
    if isinstance(lang, Rep):
        return True
    if isinstance(lang, Red):
        return is_nullable(lang.lang)


DERIVATIVES = defaultdict(dict)


def _derivative_exists(lang: Language, c) -> bool:
    if lang not in DERIVATIVES:
        return False
    if c not in DERIVATIVES[lang]:
        return False
    return True


def derive(lang: Language, c) -> Language:
    if isinstance(lang, Empty):
        return empty()
    if isinstance(lang, Epsilon):
        return empty()
    if isinstance(lang, Literal):
        return eps(lambda: [ASTChar(c)]) if lang.value == c else empty()
    if isinstance(lang, RuleLiteral):
        if not _derivative_exists(lang, c):
            DERIVATIVES[lang][c] = delay(lang, c)
        thunk: DelayRule = DERIVATIVES[lang][c]
        if thunk.is_null:
            return thunk
        else:
            return thunk.derivative
    if isinstance(lang, DelayRule):
        return derive(lang.derivative, c)
    if isinstance(lang, Concat):
        left = lang.left
        dcl_r = concat(derive(lang.left, c), lang.right)
        if is_nullable(lang.left):
            return alt(dcl_r, concat(eps(lambda: parse_null(left)), derive(lang.right, c)))
        else:
            return dcl_r
    if isinstance(lang, Alt):
        return alt(derive(lang.this, c), derive(lang.that, c))
    if isinstance(lang, Rep):
        return concat(derive(lang.lang, c), lang)
    if isinstance(lang, Red):
        return red(derive(lang.lang, c), lang.func)


def parse(lang: Language, xs):
    from functools import reduce
    return flatten_parse(collapse_parse(parse_null(reduce(derive, xs, lang))))


def parse_null(lang: Language) -> SPPF:
    if isinstance(lang, Empty):
        return []
    if isinstance(lang, Epsilon):
        return lang.func()
    if isinstance(lang, Literal):
        return []
    if isinstance(lang, RuleLiteral):
        return parse_null(lang.lang)
    if isinstance(lang, DelayRule):
        return parse_null(lang.derivative)
    if isinstance(lang, Concat):
        left_parse = parse_null(lang.left)
        if len(left_parse) == 0:
            return []
        right_parse = parse_null(lang.right)
        if len(right_parse) == 0:
            return []
        return [ASTPair(left_parse, right_parse)]
    if isinstance(lang, Alt):
        return parse_null(lang.this) + parse_null(lang.that)
    if isinstance(lang, Rep):
        return [ASTRep(parse_null(lang.lang))]
    if isinstance(lang, Red):
        return lang.func(parse_null(lang.lang))
    raise ValueError(f"unknown language: {lang}")


def flatten_parse(nodes: SPPF) -> Parse:
    seq: Parse = []

    def _flatten_parse(ns: SPPF):
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


def collapse_parse(nodes: SPPF) -> SPPF:
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
