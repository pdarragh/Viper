import viper.lexer as vl

import os
import pytest
import sys

from importlib import import_module
from typing import List, Type


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
        lexemes = vl.Lexer.lex_token(token)
    except vl.LexerError:
        assert True
    else:
        if len(lexemes) == 1:
            assert lexemes[0] != intended_type(token)
        else:
            assert True


# COMMA

def test_comma():
    lexemes = vl.Lexer.lex_token(',')
    assert len(lexemes) == 1
    assert lexemes[0] == vl.COMMA


# NUMBER

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
    '42e', '42E', '42e+', '42E+', '42e-', '42E-',
    '42.e', '42.E', '42.e+', '42.E+', '42.e-', '42.E-',
    '4.2e', '4.2E', '4.2e+', '4.2E+', '4.2e-', '4.2E-',
])
def test_bad_number(token: str):
    _test_bad_single_token(token, vl.Number)


# NAME

@pytest.mark.parametrize('token', [
    '_', '__', '___',
    'a', '_a', 'aa', 'aA', 'a1',
    'a-b-c', 'a-B-C', 'a1-b2-c3',
    'a!', 'a@', 'a$', 'a%', 'a^', 'a&', 'a*', 'a?',
])
def test_name(token: str):
    _test_single_token(token, vl.Name)


@pytest.mark.parametrize('token', [
    'A', 'AB', '-a', 'a-', 'a-b-', 'a-?', 'a?!', '42', '42e3', '?', '?!',
])
def test_bad_name(token: str):
    _test_bad_single_token(token, vl.Name)


# CLASS

@pytest.mark.parametrize('token', [
    'A', 'AB', 'AThing', 'AnotherThing', 'A-Thing', 'Another-Thing', 'Plan9', 'Plan-9-From-Outer-Space',
])
def test_class(token: str):
    _test_single_token(token, vl.Class)


@pytest.mark.parametrize('token', [
    'a-class', 'a_class', 'aA', 'A-', 'A-?', '9', '9a', '!?',
])
def test_bad_class(token: str):
    _test_bad_single_token(token, vl.Class)


# OPERATOR

@pytest.mark.parametrize('token', [
    '!', '@', '$', '%', '^', '&', '*', '-', '=', '+', '|', '/', '?', '<', '>',
    '[', ']', '{', '}', '~',
    '!@', '<>', '::', '.&',
    '(()', '()()', '())', '(())',
])
def test_operator(token: str):
    _test_single_token(token, vl.Operator)


@pytest.mark.parametrize('token', [
    'a', 'A', 'aA', 'AA', 'Aa', 'aa', '(42)', ':', '(', ')', '->', '.',
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


# OPERATORS

@pytest.mark.parametrize('line,correct_lexemes', [
    ('foo+',
     [vl.Name('foo'), vl.Operator('+')]),
    ('+foo',
     [vl.Operator('+'), vl.Name('foo')]),
    ('foo+bar',
     [vl.Name('foo'), vl.Operator('+'), vl.Name('bar')]),
    ('foo?bar',
     [vl.Name('foo'), vl.Operator('?'), vl.Name('bar')]),
    ('foo?!bar',
     [vl.Name('foo?'), vl.Operator('!'), vl.Name('bar')]),
])
def test_infix_ops(line: str, correct_lexemes: List[vl.Lexeme]):
    assert vl.lex_line(line) == correct_lexemes


# COMMAS

@pytest.mark.parametrize('line,correct_lexemes', [
    (',',
     [vl.COMMA]),
    ('foo,',
     [vl.Name('foo'), vl.COMMA]),
    ('foo,bar',
     [vl.Name('foo'), vl.COMMA, vl.Name('bar')]),
    ('foo, bar ,baz',
     [vl.Name('foo'), vl.COMMA, vl.Name('bar'), vl.COMMA, vl.Name('baz')]),
    ('foo(bar, baz)',
     [vl.Name('foo'), vl.OPEN_PAREN, vl.Name('bar'), vl.COMMA, vl.Name('baz'), vl.CLOSE_PAREN]),
    ('foo(bar,)',
     [vl.Name('foo'), vl.OPEN_PAREN, vl.Name('bar'), vl.COMMA, vl.CLOSE_PAREN]),
])
def test_commas(line: str, correct_lexemes: List[vl.Lexeme]):
    assert vl.lex_line(line) == correct_lexemes


###############################################################################
#
# LEXING TEXT
#
###############################################################################


# MULTI-LINE LEXING

@pytest.mark.parametrize('text,correct_lexemes', [
    ('\n'.join((
            'def foo(arg):',
            '    return bar()')),
     [vl.Name('def'), vl.Name('foo'), vl.OPEN_PAREN, vl.Name('arg'), vl.CLOSE_PAREN, vl.COLON,
      vl.NEWLINE,
      vl.INDENT, vl.Name('return'), vl.Name('bar'), vl.OPEN_PAREN, vl.CLOSE_PAREN,
      vl.NEWLINE]),
    ('\n'.join((
            'def foo(arg1, arg2):',
            '    return bar(arg1, arg2,)')),
     [vl.Name('def'), vl.Name('foo'), vl.OPEN_PAREN, vl.Name('arg1'), vl.COMMA, vl.Name('arg2'), vl.CLOSE_PAREN,
      vl.COLON, vl.NEWLINE,
      vl.INDENT, vl.Name('return'), vl.Name('bar'), vl.OPEN_PAREN, vl.Name('arg1'), vl.COMMA, vl.Name('arg2'),
      vl.COMMA, vl.CLOSE_PAREN, vl.NEWLINE]),
])
def test_multiple_lines(text: str, correct_lexemes: List[vl.Lexeme]):
    assert vl.Lexer.lex_lines(text) == correct_lexemes


###############################################################################
#
# FILES
#
###############################################################################


def _generate_files_and_modules():
    results = []
    cur_dir = os.path.dirname(__file__)
    viper_files_dir = os.path.join(cur_dir, 'viper_files')
    lexeme_files_dir = os.path.join(cur_dir, 'lexeme_files')
    if not os.path.isdir(viper_files_dir) or not os.path.isdir(lexeme_files_dir):
        return results
    for viper_file in (os.path.join(viper_files_dir, file) for file in os.listdir(viper_files_dir) if file.endswith('.viper')):
        basename = os.path.splitext(os.path.basename(viper_file))[0]
        if f'{basename}.py' not in os.listdir(lexeme_files_dir):
            continue
        module_name = f'.{os.path.basename(lexeme_files_dir)}.{basename}'
        results.append((viper_file, module_name))
    return results


@pytest.mark.parametrize('viper_file,module_name', _generate_files_and_modules())
def test_files(viper_file: str, module_name: str):
    module = import_module(module_name, 'tests')
    correct = module.lexemes
    lexemes = vl.lex_file(viper_file)
    assert lexemes == correct


###############################################################################
#
# MISCELLANY
#
###############################################################################


# LEXEMES

def test_lexemes():
    assert vl.Name('foo') == vl.Name('foo')
    assert vl.Indent() == vl.INDENT
    assert str(vl.Name('foo')) == 'foo'
    assert repr(vl.Name('foo')) == 'Name(foo)'
    assert repr(vl.INDENT) == 'Indent'
