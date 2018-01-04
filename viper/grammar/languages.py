from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Callable, List


Token = Any
Parse = List[Token]
PartialParse = List[Parse]


class AmbiguousParseError(Exception):
    pass


class SPPF:
    def __init__(self, *args):
        self._sppf: List[ParseTree] = list(args)

    def __eq__(self, other):
        if not isinstance(other, SPPF):
            return False
        return self._sppf == other._sppf

    def __len__(self):
        return len(self._sppf)

    def __getitem__(self, item):
        return self._sppf[item]

    def __delitem__(self, key):
        del(self._sppf[key])

    def __iter__(self):
        return iter(self._sppf)

    def __reversed__(self):
        return reversed(self._sppf)

    def __contains__(self, item):
        return item in self._sppf

    def append(self, item):
        self._sppf.append(item)

    def __add__(self, other):
        if not isinstance(other, SPPF):
            raise NotImplementedError
        return SPPF(self._sppf + other._sppf)

    def __str__(self):
        return self.make_nice_string(0)

    def __repr__(self):
        return str(self)

    def make_nice_string(self, start_column: int) -> str:
        if len(self) == 0:
            return "(empty)"
        elif len(self) == 1:
            return self[0].make_nice_string(start_column)
        else:
            leader = "(choice "
            indent = start_column + len(leader)
            lines = [leader + self[0].make_nice_string(indent)]
            for tree in self[1:]:
                line = (" " * indent) + tree.make_nice_string(indent)
                lines.append(line)
            return "\n".join(lines) + ")"


class ParseTree(ABC):
    def __str__(self):
        return self.make_nice_string(0)

    def __repr__(self):
        return str(self)

    @abstractmethod
    def __eq__(self, other):
        return False

    @abstractmethod
    def make_nice_string(self, start_column: int) -> str:
        return ""


class ParseTreeEmpty(ParseTree):
    def __eq__(self, other):
        return isinstance(other, ParseTreeEmpty)

    def make_nice_string(self, start_column: int) -> str:
        return "(empty)"


class ParseTreeChar(ParseTree):
    def __init__(self, token: Token):
        self.token = token

    def __eq__(self, other):
        if not isinstance(other, ParseTreeChar):
            return False
        return self.token == other.token

    def make_nice_string(self, start_column: int) -> str:
        return "(char " + repr(self.token) + ")"


class ParseTreePair(ParseTree):
    def __init__(self, left: SPPF, right: SPPF):
        self.left = left
        self.right = right

    def __eq__(self, other):
        if not isinstance(other, ParseTreePair):
            return False
        return self.left == other.left and self.right == other.right

    def make_nice_string(self, start_column: int) -> str:
        leader = "(pair "
        indent = start_column + len(leader)
        return (
            leader + self.left.make_nice_string(indent) + "\n" +
            (" " * indent) + self.right.make_nice_string(indent) + ")"
        )


class ParseTreeRep(ParseTree):
    def __init__(self, partial: SPPF):
        self.parse = partial

    def __eq__(self, other):
        if not isinstance(other, ParseTreeRep):
            return False
        return self.parse == other.parse

    def make_nice_string(self, start_column: int) -> str:
        leader = "(repeat "
        indent = start_column + len(leader)
        return leader + self.parse.make_nice_string(indent) + ")"


RedFunc = Callable[[SPPF], SPPF]
EpsFunc = Callable[[], SPPF]


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


def linguify(token: Token) -> Language:
    if not isinstance(token, Language):
        return literal(token)
    return token


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
                return SPPF(ParseTreePair(parse_null(l1), x))
            return red(l2, f)
        if isinstance(l2, Epsilon):
            def f(x):
                return SPPF(ParseTreePair(x, parse_null(l2)))
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
    return alt(lang, eps(lambda: SPPF(ParseTreeEmpty())))


def red(lang: Language, f: RedFunc):
    return Red(linguify(lang), f)


def is_empty(sppf: SPPF) -> bool:
    if len(sppf) == 0:
        return True
    return False


def should_delete(sppf: SPPF) -> bool:
    if len(sppf) == 1 and sppf[0] is None:
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
    raise ValueError(f"is_nullable: unknown language: {lang}")


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
        return eps(lambda: SPPF(ParseTreeChar(c))) if lang.value == c else empty()
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
        dcl_r = concat(derive(left, c), lang.right)
        if is_nullable(left):
            return alt(dcl_r, concat(eps(lambda: parse_null(left)), derive(lang.right, c)))
        else:
            return dcl_r
    if isinstance(lang, Alt):
        return alt(derive(lang.this, c), derive(lang.that, c))
    if isinstance(lang, Rep):
        return concat(derive(lang.lang, c), lang)
    if isinstance(lang, Red):
        return red(derive(lang.lang, c), lang.func)
    raise ValueError(f"derive: unknown language: {lang}")


def parse_null(lang: Language) -> SPPF:
    if isinstance(lang, Empty):
        return SPPF()
    if isinstance(lang, Epsilon):
        return lang.func()
    if isinstance(lang, Literal):
        return SPPF()
    if isinstance(lang, RuleLiteral):
        return parse_null(lang.lang)
    if isinstance(lang, DelayRule):
        return parse_null(lang.derivative)
    if isinstance(lang, Concat):
        left_parse = parse_null(lang.left)
        if len(left_parse) == 0:
            return SPPF()
        right_parse = parse_null(lang.right)
        if len(right_parse) == 0:
            return SPPF()
        return SPPF(ParseTreePair(left_parse, right_parse))
    if isinstance(lang, Alt):
        return parse_null(lang.this) + parse_null(lang.that)
    if isinstance(lang, Rep):
        return SPPF(ParseTreeRep(parse_null(lang.lang)))
    if isinstance(lang, Red):
        return lang.func(parse_null(lang.lang))
    raise ValueError(f"parse_null: unknown language: {lang}")


def collapse_parse(sppf: SPPF) -> SPPF:
    if is_empty(sppf):
        return sppf
    new_sppf = SPPF()
    # Now build a new set, eliminating any empty parses.
    for root in sppf:
        if isinstance(root, ParseTreeEmpty):
            # This should be deleted further up the tree.
            new_sppf.append(None)
        elif isinstance(root, ParseTreeChar):
            # Always add terminals.
            new_sppf.append(root)
        elif isinstance(root, ParseTreePair):
            left = collapse_parse(root.left)
            right = collapse_parse(root.right)
            if should_delete(left):
                # Delete left.
                if should_delete(right):
                    # Delete both.
                    continue
                else:
                    # Delete left, not right.
                    new_sppf += right
            else:
                # Don't delete left.
                if not should_delete(right):
                    # Don't delete right.
                    if not (is_empty(left) or is_empty(right)):
                        # Add only if neither part of the sequence is empty.
                        new_sppf.append(ParseTreePair(left, right))
                else:
                    # Delete right, not left.
                    new_sppf += left
        elif isinstance(root, ParseTreeRep):
            # Always add the ASTRep, even if its interior parse comes up empty.
            # This ensures we can properly parse repeated tokens.
            new_sppf.append(ParseTreeRep(collapse_parse(root.parse)))
    if len(new_sppf) > 1:  # TODO: consider making a toggle
        raise AmbiguousParseError
    return new_sppf


def make_sppf(lang: Language, tokens: List[Token]) -> SPPF:
    from functools import reduce
    return collapse_parse(parse_null(reduce(derive, tokens, lang)))


def print_lang(lang: Language):
    print(_make_nice_lang_string(lang, 0))


def _make_nice_lang_string(lang: Language, start_column: int):
    if isinstance(lang, Empty):
        return "(empty)"
    if isinstance(lang, Epsilon):
        return "(epsilon)"
    if isinstance(lang, Literal):
        return "(literal " + repr(lang.value) + ")"
    if isinstance(lang, RuleLiteral):
        return "(rule <" + lang.name + ">)"
    if isinstance(lang, DelayRule):
        return "(delay <" + lang.lang.name + "> [" + ("unforced" if lang.is_null else "forced") + "])"
    if isinstance(lang, Concat):
        leader = "(concat "
        indent = start_column + len(leader)
        return (
            leader + _make_nice_lang_string(lang.left, indent) + "\n" +
            (" " * indent) + _make_nice_lang_string(lang.right, indent) + ")"
        )
    if isinstance(lang, Alt):
        leader = "(union "
        indent = start_column + len(leader)
        return (
            leader + _make_nice_lang_string(lang.this, indent) + "\n" +
            (" " * indent) + _make_nice_lang_string(lang.that, indent) + ")"
        )
    if isinstance(lang, Rep):
        leader = "(repeat "
        indent = start_column + len(leader)
        return leader + _make_nice_lang_string(lang.lang, indent) + ")"
    if isinstance(lang, Red):
        leader = "(reduce "
        indent = start_column + len(leader)
        return leader + _make_nice_lang_string(lang.lang, indent) + ")"
    raise ValueError
