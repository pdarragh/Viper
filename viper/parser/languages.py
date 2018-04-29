from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Callable, List


Token = Any
Parse = List[Token]
PartialParse = List[Parse]


class SPPF:
    def __init__(self, *args):
        self._sppf: List[ParseTree] = []
        for arg in args:
            self._sppf.append(arg)

    def __eq__(self, other):
        if not isinstance(other, SPPF):
            return False
        return self._sppf == other._sppf

    def __len__(self):
        return len(self._sppf)

    def __bool__(self):
        return len(self) > 0

    def __getitem__(self, item):
        return self._sppf[item]

    def __iter__(self):
        return iter(self._sppf)

    def append(self, item):
        if not isinstance(item, ParseTree):
            raise ValueError(f"invalid argument to SPPF.append: {item}")
        self._sppf.append(item)

    def __add__(self, other):
        if not isinstance(other, SPPF):
            raise NotImplementedError
        from itertools import chain
        result = SPPF()
        new_list = []
        for item in chain(self._sppf, other._sppf):
            new_list.append(item)
        result._sppf = new_list
        return result

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


EpsFunc = Callable[[], SPPF]


class RedFunc(Callable[[SPPF], SPPF]):
    @abstractmethod
    def __call__(self, sppf: SPPF) -> SPPF:
        pass

    def __repr__(self):
        return self.make_nice_string(0)

    @abstractmethod
    def make_nice_string(self, start_column: int) -> str:
        pass


class LeftEpsRedFunc(RedFunc):
    def __init__(self, left: SPPF):
        self.left = left

    def make_nice_string(self, start_column: int) -> str:
        return self.left.make_nice_string(start_column)

    def __call__(self, right: SPPF) -> SPPF:
        return SPPF(ParseTreePair(self.left, right))


class RightEpsRedFunc(RedFunc):
    def __init__(self, right: SPPF):
        self.right = right

    def make_nice_string(self, start_column: int) -> str:
        return self.right.make_nice_string(start_column)

    def __call__(self, left: SPPF) -> SPPF:
        return SPPF(ParseTreePair(left, self.right))


class RepRedFunc(RedFunc):
    def make_nice_string(self, start_column: int) -> str:
        return self.repr_string

    def __init__(self, repr_string: str):
        self.repr_string = repr_string

    def __call__(self, sppf: SPPF) -> SPPF:
        if len(sppf) == 0:
            return SPPF()
        elif len(sppf) == 1:
            child = sppf[0]
            if isinstance(child, ParseTreeEps):
                return SPPF(ParseTreeChar([]))
            elif isinstance(child, ParseTreeChar):
                return SPPF(ParseTreeChar([child.token]))
            elif isinstance(child, ParseTreePair):
                accum = []
                curr = child
                while isinstance(curr, ParseTreePair):
                    inner_child_sppf: SPPF = curr.left
                    if len(inner_child_sppf) == 0:
                        return SPPF()
                    elif len(inner_child_sppf) == 1:
                        inner_child = inner_child_sppf[0]
                        if not isinstance(inner_child, ParseTreeChar):
                            raise RuntimeError(f"Invalid inner child of list-rep reduction: {curr.left}")
                        accum.append(inner_child.token)
                        inner_sppf: SPPF = curr.right
                        if len(inner_sppf) == 0:
                            return SPPF()
                        elif len(inner_sppf) == 1:
                            curr = inner_sppf[0]
                        else:
                            raise RuntimeError("Too many children in inner-inner list-rep reduction target.")
                    else:
                        raise RuntimeError("Too many children in inner list-rep reduction target.")
                if isinstance(curr, ParseTreeEmpty):
                    return SPPF()
                elif isinstance(curr, ParseTreeEps):
                    return SPPF(ParseTreeChar(accum))
                else:
                    raise RuntimeError("Invalid inner list-rep reduction target.")
            else:
                raise RuntimeError("Invalid list-rep reduction target.")
        else:
            raise RuntimeError("Too many children from list-rep reduction.")


class SepRepRedFunc(RepRedFunc):
    def __init__(self):
        super().__init__('&')


class ListRepRedFunc(RepRedFunc):
    def __init__(self):
        super().__init__('*')


class MinRepRedFunc(RedFunc):
    def make_nice_string(self, start_column: int) -> str:
        return "+"

    def __call__(self, sppf: SPPF) -> SPPF:
        if len(sppf) == 0:
            return SPPF()
        elif len(sppf) == 1:
            child = sppf[0]
            if not isinstance(child, ParseTreePair):
                raise RuntimeError("Invalid min-rep child.")
            left_sppf = child.left
            if len(left_sppf) == 0:
                return SPPF()
            elif len(left_sppf) == 1:
                left_child = left_sppf[0]
                if not isinstance(left_child, ParseTreeChar):
                    raise RuntimeError("Invalid left child of min-rep reduction.")
                left = left_child.token
            else:
                raise RuntimeError("Too many children in left child of min-rep reduction.")
            right_sppf = child.right
            # The right child should always reduce to a list.
            if len(right_sppf) == 0:
                # There was only one element in the list.
                return SPPF(ParseTreeChar([left]))
            elif len(right_sppf) == 1:
                right_child = right_sppf[0]
                if not isinstance(right_child, ParseTreeChar):
                    raise RuntimeError("Invalid right child of min-rep reduction.")
                right = right_child.token
            else:
                raise RuntimeError("Too many children in right child of min-rep reduction.")
            return SPPF(ParseTreeChar([left] + right))
        else:
            raise RuntimeError("Too many children for min-rep reduction.")


class SepRepEpsRedFunc(RedFunc):
    def make_nice_string(self, start_column: int) -> str:
        return "sep-rep epsilon"

    def __call__(self, sppf: SPPF) -> SPPF:
        if len(sppf) == 0:
            return SPPF()
        elif len(sppf) == 1:
            return SPPF(ParseTreeEps())
        else:
            raise RuntimeError("Epsilon produced multiple results.")


class SepRepConcatRedFunc(RedFunc):
    def make_nice_string(self, start_column: int) -> str:
        return "sep-rep concat"

    def __call__(self, sppf: SPPF) -> SPPF:
        if len(sppf) == 0:
            return SPPF()
        elif len(sppf) == 1:
            child = sppf[0]
            if not isinstance(child, ParseTreePair):
                raise RuntimeError("Invalid concat child.")
            return child.right
        else:
            raise RuntimeError("Too many children from concat reduction.")


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


class ParseTreeEps(ParseTree):
    def __eq__(self, other):
        return isinstance(other, ParseTreeEps)

    def make_nice_string(self, start_column: int) -> str:
        return "(eps)"


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
            return repr(self.left) + " ◦ " + repr(self.right)
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
        return "⌊" + repr(self.lang) + " --> " + repr(self.func) + "⌋"

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


def empty() -> Language:
    return Empty()


def eps(func: EpsFunc) -> Language:
    return Epsilon(func)


def literal(c) -> Language:
    return Literal(c)


def delay(rl: RuleLiteral, c) -> Language:
    return DelayRule(rl, c)


def concat(l1: Language, *ls: Language) -> Language:
    l1 = linguify(l1)
    if len(ls) == 0:
        return l1
    elif len(ls) == 1:
        l2 = linguify(ls[0])
        if isinstance(l1, Empty) or isinstance(l2, Empty):
            return empty()
        if isinstance(l1, Epsilon):
            return red(l2, LeftEpsRedFunc(parse_null(l1)))
        if isinstance(l2, Epsilon):
            return red(l1, RightEpsRedFunc(parse_null(l2)))
        return Concat(l1, l2)
    else:
        return Concat(l1, concat(*ls))


def alt(l1: Language, *ls: Language) -> Language:
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


def rep(lang: Language) -> Language:
    return Rep(linguify(lang))


def list_rep(lang: Language) -> Language:
    return red(Rep(linguify(lang)), ListRepRedFunc())


def min_rep(lang: Language) -> Language:
    """
    A minimum-repeat, i.e. w+.

    Constructed as:

          ◦
         / \
        w   *
            |
            w
    """
    return red(concat(lang, list_rep(lang)), MinRepRedFunc())


def sep_rep(sep_lang: Language, lang: Language) -> Language:
    """
    A separated-repeat, e.g. for matching things like:

        w s w s w

    (where "w" is the item to be matched and "s" is a separator to be discarded).

    Constructed as:

          ∪
         / \
        ε   ◦
           / \
          w   *
              |
              ◦
             / \
            s   w
    """
    return red(alt(red(eps(lambda: SPPF(ParseTreeEps())), SepRepEpsRedFunc()),
                   concat(lang, rep(red(concat(sep_lang, lang), SepRepConcatRedFunc())))),
               SepRepRedFunc())


def min_sep_rep(sep_lang: Language, lang: Language) -> Language:
    """
    Like a sep-rep, but requires at least one instance of `lang`.

    Constructed as:

        ◦
       / \
      w   *
          |
          ◦
         / \
        s   w
    """
    return red(concat(lang, rep(red(concat(sep_lang, lang), SepRepConcatRedFunc()))),
               SepRepRedFunc())


def opt(lang: Language) -> Language:
    return alt(lang, eps(lambda: SPPF(ParseTreeEps())))


def red(lang: Language, f: RedFunc) -> Language:
    return Red(linguify(lang), f)


def is_empty(sppf: SPPF) -> bool:
    return len(sppf) == 0


def is_eps(sppf: SPPF) -> bool:
    return len(sppf) == 1 and isinstance(sppf[0], ParseTreeEps)


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
        inner = derive(lang.lang, c)
        if isinstance(inner, Empty):
            return empty()
        else:
            return red(inner, lang.func)
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
        if is_empty(left_parse):
            return SPPF()
        right_parse = parse_null(lang.right)
        if is_empty(right_parse):
            return SPPF()
        return SPPF(ParseTreePair(left_parse, right_parse))
    if isinstance(lang, Alt):
        this_parse = parse_null(lang.this)
        that_parse = parse_null(lang.that)
        if is_empty(this_parse):
            return that_parse
        else:
            if is_empty(that_parse):
                return this_parse
            else:
                return this_parse + that_parse
    if isinstance(lang, Rep):
        rep_parse = parse_null(lang.lang)
        if is_empty(rep_parse):
            # Repeats produce epsilons instead of empties due to nullability.
            return SPPF(ParseTreeEps())
        else:
            return SPPF(ParseTreeRep(rep_parse))
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
            # Empty parses should remain empty.
            pass
        elif isinstance(root, ParseTreeEps):
            # Epsilons are needed for proper pair reduction.
            new_sppf.append(root)
        elif isinstance(root, ParseTreeChar):
            # Always add terminals.
            new_sppf.append(root)
        elif isinstance(root, ParseTreePair):
            left = collapse_parse(root.left)
            right = collapse_parse(root.right)
            if is_empty(left) or is_empty(right):
                # Pairs must have two non-empty children.
                pass
            else:
                # If either side is an epsilon, the pair can be reduced.
                if is_eps(left):
                    if is_eps(right):
                        new_sppf.append(ParseTreeEps())
                    else:
                        for item in right:
                            new_sppf.append(item)
                        # new_sppf.append(right)
                else:
                    if is_eps(right):
                        for item in left:
                            new_sppf.append(item)
                        # new_sppf.append(left)
                    else:
                        new_sppf.append(ParseTreePair(left, right))
        elif isinstance(root, ParseTreeRep):
            # Always add the ASTRep, even if its interior parse comes up empty.
            # This ensures we can properly parse repeated tokens.
            collapsed = collapse_parse(root.parse)
            if is_empty(collapsed):
                new_sppf.append(ParseTreeEps())
            else:
                new_sppf.append(ParseTreeRep(collapsed))
        else:
            raise ValueError(f"collapse_parse: unknown ParseTree node: {root}")
    return new_sppf


def make_sppf(lang: Language, tokens: List[Token]) -> SPPF:
    from functools import reduce
    return collapse_parse(parse_null(reduce(derive, tokens, lang)))


def print_lang(lang: Language):
    print(_make_nice_lang_string(lang, 0))


def _make_nice_lang_string(lang: Language, start_column: int) -> str:
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
        return (
            leader + _make_nice_lang_string(lang.lang, indent) + "\n" +
            (" " * indent) + "-> " + lang.func.make_nice_string(indent) + ")"
        )
    raise ValueError(f"Unknown language type: {lang}")
