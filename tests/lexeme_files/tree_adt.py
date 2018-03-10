from viper.lexer import (
    NEWLINE as NL, INDENT as IND, DEDENT as DED, COLON, OPEN_PAREN as OP, CLOSE_PAREN as CP,
    Name as N,
    Class as C,
)


lexemes = [
    N('data'), C('Tree'), OP, N('a'), CP, COLON,
    NL, IND, C('Leaf'), N('a'),
    NL, IND, C('Branch'), OP, C('Tree'), N('a'), CP, OP, C('Tree'), N('a'), CP, DED,
]
