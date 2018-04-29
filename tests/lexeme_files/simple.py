from viper.lexer import (
    NEWLINE as NL, INDENT as IND, DEDENT as DED, COLON as COL, COMMA as COM, OPEN_PAREN as OP, CLOSE_PAREN as CP,
    ENDMARKER as EM, R_ARROW as ARR,
    Number as Num,
    Name as N, ReservedName as RN,
    Class as C,
    Operator as Op,
)

lexemes = [
    RN('def'), N('simple'), OP, N('foo'), COL, C('A'), COM, N('bar'), COL, C('B'), CP, ARR, C('C'), COL,
    NL, IND,
        N('foo'), Op('='), N('bar'), Op('+'), Num('42'), NL,
        N('bar'), Op('*='), Num('17'), NL,
        RN('return'), N('foo'), Op('>=>'), N('bar'), NL,
    DED,
    EM,
]
