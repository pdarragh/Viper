from viper.lexer import (
    NEWLINE as NL, INDENT as IND, DEDENT as DED, COLON as COL, OPEN_PAREN as OP, CLOSE_PAREN as CP, ENDMARKER as EM,
    R_ARROW as R_ARR, L_ARROW as L_ARR,
    Name as N, ReservedName as RN,
    Class as C,
)

lexemes = [
    RN('def'), N('func'), OP, N('x'), COL, C('Int'), CP, R_ARR, C('Int'), COL,
    NL, IND,
        RN('for'), N('y'), L_ARR, N('range'), OP, N('x'), CP, COL,
        NL, IND,
            N('print'), OP, N('y'), CP, NL,
        DED,
    DED,
    EM,
]
