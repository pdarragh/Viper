from viper.lexer import (
    NEWLINE, INDENT, COLON, OPEN_PAREN as OP, CLOSE_PAREN as CP,
    Name as N,
    Class as C,
)


lexemes = [
    N('data'), C('Tree'), OP, N('a'), CP, COLON, NEWLINE,
    INDENT, C('Leaf'), N('a'), NEWLINE,
    INDENT, C('Branch'), OP, C('Tree'), N('a'), CP, OP, C('Tree'), N('a'), CP, NEWLINE
]
