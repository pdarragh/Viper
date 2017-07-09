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


def lit(val):
    return Literal(val)


def gl(val):
    return lit(GrammarLiteral(val))


def r(rule):
    return RuleLiteral(rule, GRAMMAR_DICT)


INDENT = GrammarToken(vl.Indent)
DEDENT = GrammarToken(vl.Dedent)
NEWLINE = GrammarToken(vl.NewLine)
PERIOD = GrammarToken(vl.Period)
COMMA = GrammarToken(vl.Comma)
OPEN_PAREN = GrammarToken(vl.OpenParen)
CLOSE_PAREN = GrammarToken(vl.CloseParen)
COLON = GrammarToken(vl.Colon)
ARROW = GrammarToken(vl.Arrow)
NUMBER = GrammarToken(vl.Number)
NAME = GrammarToken(vl.Name)
CLASS = GrammarToken(vl.Class)
OPERATOR = GrammarToken(vl.Operator)


GRAMMAR_DICT.update({
    'type_expr':     lit(CLASS),

    'func_def':      Concat(gl('def'), r('func_name'), r('parameters'), lit(ARROW), r('func_type'), lit(COLON), r('suite')),
    'func_name':     lit(NAME),
    'func_type':     r('type_expr'),

    'parameters':    Concat(lit(OPEN_PAREN), Optional(r('params_list')), lit(CLOSE_PAREN)),
    'params_list':   Union(r('parameter'),
                           Concat(r('parameter'), r('params_list'))),
    'parameter':     Concat(Optional(r('ext_label')), r('local_label'), r('param_type')),
    'ext_label':     lit(NAME),
    'local_label':   lit(NAME),
    'param_type':    r('type_expr'),

    'suite':         Union(r('simple_stmt'),
                           Concat(lit(NEWLINE), lit(INDENT), r('stmt'), Repeat(r('stmt')), lit(DEDENT))),

    'stmt':          Union(r('simple_stmt'),
                           r('compound_stmt')),

    'simple_stmt':   Concat(r('expr_stmt'), lit(NEWLINE)),
    'expr_stmt':     Union(r('expr_list'),
                           gl('pass'),
                           Concat(gl('return'), Optional(r('expr_list')))),
    'expr_list':     Union(r('expr'),
                           Concat(r('expr'), lit(COMMA), r('expr_list'))),

    'expr':          Concat(r('atom'), r('trailer_list')),
    'atom':          Union(Concat(lit(OPEN_PAREN), Optional(r('expr_list')), lit(CLOSE_PAREN)),
                           lit(NAME),
                           lit(NUMBER),
                           gl('...'),
                           gl('Zilch'),
                           gl('True'),
                           gl('False')),
    'trailer_list':  Union(r('trailer'),
                           Concat(r('trailer'), r('trailer_list'))),
    'trailer':       Union(Concat(lit(OPEN_PAREN), Optional(r('arg_list')), lit(CLOSE_PAREN)),
                           Concat(lit(PERIOD), lit(NAME))),

    'compound_stmt': Union(r('func_def'),
                           r('object_def'),
                           r('data_def')),

    'object_def':    Union(r('class_def'),
                           r('interface_def'),
                           r('data_def')),

    'class_def':     Concat(gl('class'), r('common_def')),
    'interface_def': Concat(gl('interface'), r('common_def')),
    'data_def':      Concat(gl('data'), r('common_def')),
    'common_def':    Concat(lit(NAME), Optional(r('arguments')), lit(COLON), r('suite')),
    'arguments':     Concat(lit(OPEN_PAREN), Optional(r('arg_list')), lit(CLOSE_PAREN)),
    'arg_list':      Union(r('argument'),
                           Concat(r('argument'), lit(COMMA), r('arg_list'))),
    'argument':      r('expr'),
})


GRAMMAR = Union(*GRAMMAR_DICT.values())
