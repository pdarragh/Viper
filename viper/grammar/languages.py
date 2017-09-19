# Copied from my implementation at:
#   https://github.com/pdarragh/Personal/blob/master/Python/PWD.py

from abc import ABC, abstractmethod
from typing import List


class Language(ABC):
    def __str__(self):
        return '<Language>'

    def __repr__(self):
        return str(self)

    @abstractmethod
    def __nullable__(self) -> bool:
        return False

    @abstractmethod
    def __derive__(self, c):
        return EMPTY

    def pretty_print(self):
        print(format_language(self))


def nullable(language: Language):
    return language.__nullable__()


def derive(language: Language, c):
    return language.__derive__(c)


class Empty(Language):
    def __eq__(self, other):
        return isinstance(other, Empty)

    def __str__(self):
        return '∅'

    def __nullable__(self):
        return False

    def __derive__(self, c):
        return EMPTY


class Epsilon(Language):
    def __eq__(self, other):
        return isinstance(other, Epsilon)

    def __str__(self):
        return 'ε'

    def __nullable__(self):
        return True

    def __derive__(self, c):
        return EMPTY


class Literal(Language):
    def __new__(cls, lit):
        if isinstance(lit, Literal):
            return lit
        new_self = super().__new__(cls)
        new_self.lit = lit
        return new_self

    def __eq__(self, other):
        if not isinstance(other, Literal):
            return False
        return self.lit == other.lit

    def __str__(self):
        return str(self.lit)

    def __nullable__(self):
        return False

    def __derive__(self, c):
        return EPSILON if self.lit == c else EMPTY


def linguify(x) -> Language:
    if not isinstance(x, Language):
        return Literal(x)
    return x


class Union(Language):
    def __new__(cls, l1: Language, *ls: Language):
        l1 = linguify(l1)
        if len(ls) == 0:
            return l1
        if isinstance(l1, Empty):
            return Union(*ls)
        if isinstance(l1, Epsilon) and isinstance(ls[0], Epsilon):
            return Union(EPSILON, *ls[1:])
        if isinstance(l1, Union):
            return Union(l1.head, Union(l1.tail, *ls))
        tail = Union(*ls)
        if isinstance(tail, Empty):
            return l1
        new_self = super().__new__(cls)
        new_self.head = l1
        new_self.tail = tail
        return new_self

    def __eq__(self, other):
        if not isinstance(other, Union):
            return False
        return self.head == other.head and self.tail == other.tail

    def __str__(self):
        if isinstance(self.head, Epsilon):
            return f'{str(self.tail)}?'
        elif isinstance(self.tail, Epsilon):
            return f'{str(self.head)}?'
        else:
            tail_string = str(self.tail)
            if isinstance(self.tail, Union):
                tail_string = tail_string[1:-1]
            return f'[{str(self.head)} + {str(tail_string)}]'

    def __nullable__(self):
        return nullable(self.head) or nullable(self.tail)

    def __derive__(self, c):
        return Union(derive(self.head, c), derive(self.tail, c))


class Concat(Language):
    def __new__(cls, l1: Language, *ls: Language):
        l1 = linguify(l1)
        if len(ls) == 0:
            return l1
        if isinstance(l1, Empty):
            return EMPTY
        if isinstance(l1, Epsilon):
            return Concat(*ls)
        if isinstance(l1, Concat):
            return Concat(l1.head, Concat(l1.tail, *ls))
        new_self = super().__new__(cls)
        new_self.head = l1
        new_self.tail = Concat(*ls)
        return new_self

    def __eq__(self, other):
        if not isinstance(other, Concat):
            return False
        return self.head == other.head and self.tail == other.tail

    def __str__(self):
        return f'({str(self.head)} {str(self.tail)})'

    def __nullable__(self):
        return nullable(self.head) and nullable(self.tail)

    def __derive__(self, c):
        d = Concat(derive(self.head, c), self.tail)
        if nullable(self.head):
            return Union(d, derive(self.tail, c))
        else:
            return d


class Repeat(Language):
    def __new__(cls, l1: Language, *ls: Language):
        l1 = linguify(l1)
        if len(ls) > 0:
            return Repeat(Concat(l1, *ls))
        if isinstance(l1, Empty):
            return EMPTY
        if isinstance(l1, Epsilon):
            return EPSILON
        if isinstance(l1, Repeat):
            return l1
        new_self = super().__new__(cls)
        new_self.lang = l1
        return new_self

    def __eq__(self, other):
        if not isinstance(other, Repeat):
            return False
        return self.lang == other.lang

    def __str__(self):
        return f'({str(self.lang)})*'

    def __nullable__(self):
        return True

    def __derive__(self, c):
        return Concat(derive(self.lang, c), self)


class Optional(Language):
    def __new__(cls, l1: Language, *ls: Language):
        l1 = linguify(l1)
        if len(ls) > 0:
            return Optional(Concat(l1, *ls))
        return Union(l1, EPSILON)

    def __nullable__(self) -> bool:
        pass

    def __derive__(self, c):
        pass


EMPTY = Empty()
EPSILON = Epsilon()


def stringify_language(l: Language) -> List[str]:
    from itertools import chain
    if isinstance(l, Union):
        result = []
        for s in chain(stringify_language(l.head), stringify_language(l.tail)):
            result.append(s)
        return result
    if isinstance(l, Concat):
        result = []
        for s1 in stringify_language(l.head):
            for s2 in stringify_language(l.tail):
                result.append(f'{s1} {s2}')
        return result
    return [str(l)]


def format_language(l: Language) -> str:
    result = []
    strings = stringify_language(l)
    for i, s in enumerate(strings):
        result.append(f'{i:>{len(str(len(strings)-1))}}. {s}')
    return '\n'.join(result)
