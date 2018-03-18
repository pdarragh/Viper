from viper.lexer import (
    NEWLINE as NL, INDENT as IND, DEDENT as DED, COLON, OPEN_PAREN as OP, CLOSE_PAREN as CP, ENDMARKER as EM,
    Name as N, ReservedName as RN,
    Class as C,
)


lexemes = [
    RN('data'), C('Tree'), OP, N('a'), CP, COLON,
    NL, IND,
        C('Leaf'), N('a'), NL,
        C('Branch'), OP, C('Tree'), N('a'), CP, OP, C('Tree'), N('a'), CP, NL,
    DED,
    EM,
]
