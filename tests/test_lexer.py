import viper.lexer as vl

import pytest

from typing import Type


###############################################################################
#
# INDIVIDUAL TOKENS
#
###############################################################################


def _test_single_token(token: str, lexeme_type: Type):
    lexemes = vl.Lexer.lex_token(token)
    assert len(lexemes) == 1
    assert lexemes[0] == lexeme_type(token)


def _test_bad_single_token(token: str, intended_type: Type):
    try:
        _test_single_token(token, intended_type)
    except AssertionError:
        assert True
    except vl.LexerError:
        assert True


# CORRECT TOKENS
#
# These tests should test all types of different tokens for each form of
# lexeme.

@pytest.mark.parametrize('token', [
    '42',
    '.42', '.42e8', '.42E8', '.42e+8', '.42E+8', '.42e-8', '.42E-8',
    '42e8', '42E8', '42e+8', '42E+8', '42e-8', '42E-8',
    '42.', '42.e8', '42.E8', '42.e+8', '42.E+8', '42.e-8', '42.E-8',
    '4.2', '4.2e8', '4.2E8', '4.2e+8', '4.2E+8', '4.2e-8', '4.2E-8',
])
def test_number(token: str):
    _test_single_token(token, vl.Number)


@pytest.mark.parametrize('token', [
    '_', '__', '___',
    'a', '_a', 'aa', 'aA', 'a1',
    'a-b-c', 'a-B-C', 'a1-b2-c3',
    'a!', 'a@', 'a$', 'a%', 'a^', 'a&', 'a*', 'a?',
])
def test_name(token: str):
    _test_single_token(token, vl.Name)


@pytest.mark.parametrize('token', [
    'A', 'AB', 'AThing', 'AnotherThing', 'A-Thing', 'Another-Thing', 'Plan9', 'Plan-9-From-Outer-Space',
])
def test_class(token: str):
    _test_single_token(token, vl.Class)


@pytest.mark.parametrize('token', [
    '!', '@', '$', '%', '^', '&', '*', '(', ')', '-', '=', '+', '|', ':', '/', '?', '<', '>',
    '[', ']', '{', '}', '~',
    '!@', '<>', '::',
    '()', '(()', '()()', '())', '(())',
])
def test_operator(token: str):
    _test_single_token(token, vl.Operator)


# INCORRECT TOKENS
#
# These tests should ensure that rogue tokens do not sneak through.

@pytest.mark.parametrize('token', [
    '42e', '42E', '42e+', '42E+', '42e-', '42E-',
    '42.e', '42.E', '42.e+', '42.E+', '42.e-', '42.E-',
    '4.2e', '4.2E', '4.2e+', '4.2E+', '4.2e-', '4.2E-',
])
def test_bad_number(token: str):
    _test_bad_single_token(token, vl.Number)


@pytest.mark.parametrize('token', [
    'A', 'AB', '-a', 'a-', 'a-b-', 'a-?', 'a?!', '42', '42e3', '?', '?!',
])
def test_bad_name(token: str):
    _test_bad_single_token(token, vl.Name)


@pytest.mark.parametrize('token', [
    'a-class', 'a_class', 'aA', '9', '9a', '!?',
])
def test_bad_class(token: str):
    _test_bad_single_token(token, vl.Class)


@pytest.mark.parametrize('token', [
    'a', 'A', 'aA', 'AA', 'Aa', 'aa', '(42)',
])
def test_bad_operator(token: str):
    _test_bad_single_token(token, vl.Operator)


###############################################################################
#
# LEXING LINES
#
###############################################################################


# INDENTATION

@pytest.mark.parametrize('levels', [
    0, 1, 2, 3, 4,
])
def test_indentation(levels: int):
    line = ''.join(' ' * vl.INDENT_SIZE for _ in range(levels))
    correct = [vl.INDENT for _ in range(levels)]
    assert vl.lex_line(line) == correct


@pytest.mark.parametrize('line,indent_count', [
    ('none', 0),
    ('    one', 1),
    ('        two', 2),
    ('     one plus space', 1),
])
def test_leading_indentation(line: str, indent_count: int):
    lexemes = vl.lex_line(line)
    assert len(lexemes) >= indent_count
    indents = lexemes[:indent_count]
    rest = lexemes[indent_count:]
    for indent in indents:
        assert indent == vl.INDENT
    if rest:
        assert rest[0] != vl.INDENT
