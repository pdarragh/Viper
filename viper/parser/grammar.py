from viper.parser.languages import *

import viper.lexer as vl

from typing import ClassVar


class GrammarToken:
    def __init__(self, lexeme_class: ClassVar):
        self._lexeme_class = lexeme_class

    def __eq__(self, other):
        if isinstance(other, GrammarToken):
            return self._lexeme_class == other._lexeme_class
        elif isinstance(other, Literal):
            return other.lit == self
        return isinstance(other, self._lexeme_class)


class GrammarLiteral:
    def __init__(self, val: str):
        self._val = val

    def __eq__(self, other):
        if isinstance(other, GrammarLiteral):
            return self._val == other._val
        if isinstance(other, vl.Lexeme):
            return self._val == other.text
        return False


class RuleLiteral(Language):
    def __init__(self, rule: str, grammar):
        self.rule = rule
        self.grammar = grammar

    def __eq__(self, other):
        if isinstance(other, RuleLiteral):
            return self.rule == other.rule
        if isinstance(other, Language):
            return self.grammar[self.rule] == other
        return False

    def __str__(self):
        return f'<{self.rule}>'

    def __nullable__(self) -> bool:
        return nullable(self.grammar[self.rule])

    def __derive__(self, c):
        return derive(self.grammar[self.rule], c)


GRAMMAR_DICT = {}


def gl(val):
    return Literal(GrammarLiteral(val))


def r(rule):
    return RuleLiteral(rule, GRAMMAR_DICT)


INDENT = Literal(GrammarToken(vl.Indent))
DEDENT = Literal(GrammarToken(vl.Dedent))
NEWLINE = Literal(GrammarToken(vl.NewLine))
PERIOD = Literal(GrammarToken(vl.Period))
COMMA = Literal(GrammarToken(vl.Comma))
OPEN_PAREN = Literal(GrammarToken(vl.OpenParen))
CLOSE_PAREN = Literal(GrammarToken(vl.CloseParen))
COLON = Literal(GrammarToken(vl.Colon))
ARROW = Literal(GrammarToken(vl.Arrow))
NUMBER = Literal(GrammarToken(vl.Number))
NAME = Literal(GrammarToken(vl.Name))
CLASS = Literal(GrammarToken(vl.Class))
OPERATOR = Literal(GrammarToken(vl.Operator))


GRAMMAR_DICT.update({
    'type_expr':     CLASS,

    'func_def':      Concat(gl('def'), r('func_name'), r('parameters'), ARROW, r('func_type'), COLON, r('suite')),
    'func_name':     NAME,
    'func_type':     r('type_expr'),

    'parameters':    Concat(OPEN_PAREN, Optional(r('params_list')), CLOSE_PAREN),
    'params_list':   Union(r('parameter'),
                           Concat(r('parameter'), r('params_list'))),
    'parameter':     Concat(Optional(r('ext_label')), r('local_label'), r('param_type')),
    'ext_label':     NAME,
    'local_label':   NAME,
    'param_type':    r('type_expr'),

    'suite':         Union(r('simple_stmt'),
                           Concat(NEWLINE, INDENT, r('stmt'), Repeat(r('stmt')), DEDENT)),

    'stmt':          Union(r('simple_stmt'),
                           r('compound_stmt')),

    'simple_stmt':   Concat(r('expr_stmt'), NEWLINE),
    'expr_stmt':     Union(r('expr_list'),
                           gl('pass'),
                           Concat(gl('return'), Optional(r('expr_list')))),
    'expr_list':     Union(r('expr'),
                           Concat(r('expr'), COMMA, r('expr_list'))),

    'expr':          Concat(r('atom'), r('trailer_list')),
    'atom':          Union(Concat(OPEN_PAREN, Optional(r('expr_list')), CLOSE_PAREN),
                           NAME,
                           NUMBER,
                           gl('...'),
                           gl('Zilch'),
                           gl('True'),
                           gl('False')),
    'trailer_list':  Union(r('trailer'),
                           Concat(r('trailer'), r('trailer_list'))),
    'trailer':       Union(Concat(OPEN_PAREN, Optional(r('arg_list')), CLOSE_PAREN),
                           Concat(PERIOD, NAME)),

    'compound_stmt': Union(r('func_def'),
                           r('object_def'),
                           r('data_def')),

    'object_def':    Union(r('class_def'),
                           r('interface_def'),
                           r('data_def')),

    'class_def':     Concat(gl('class'), r('common_def')),
    'interface_def': Concat(gl('interface'), r('common_def')),
    'data_def':      Concat(gl('data'), r('common_def')),
    'common_def':    Concat(NAME, Optional(r('arguments')), COLON, r('suite')),
    'arguments':     Concat(OPEN_PAREN, Optional(r('arg_list')), CLOSE_PAREN),
    'arg_list':      Union(r('argument'),
                           Concat(r('argument'), COMMA, r('arg_list'))),
    'argument':      r('expr'),
})


GRAMMAR = Union(*GRAMMAR_DICT.values())
