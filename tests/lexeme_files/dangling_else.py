from viper.lexer import (
    NEWLINE as NL, INDENT as IND, DEDENT as DED, COLON as COL, OPEN_PAREN as OP, CLOSE_PAREN as CP, ENDMARKER as EM,
    R_ARROW as ARR,
    Int,
    Name as N, ReservedName as RN,
    Class as C,
    Operator as Op,
)

lexemes = [
    RN('def'), N('func1'), OP, N('x'), COL, C('Int'), CP, ARR, C('Int'), COL,
    NL, IND,
        RN('if'), N('x'), Op('>'), Int('1'), COL,
        NL, IND,
            RN('if'), N('x'), Op('>'), Int('2'), COL,
            NL, IND,
                RN('return'), Int('9'), NL,
            DED,
        DED,
        RN('else'), COL,
        NL, IND,
            RN('return'), Int('19'), NL,
        DED,
    DED,
    RN('def'), N('func2'), OP, N('x'), COL, C('Int'), CP, ARR, C('Int'), COL,
    NL, IND,
        RN('if'), N('x'), Op('>'), Int('1'), COL,
        NL, IND,
            RN('if'), N('x'), Op('>'), Int('2'), COL,
            NL, IND,
                RN('return'), Int('9'), NL,
            DED,
            RN('else'), COL,
            NL, IND,
                RN('return'), Int('42'), NL,
            DED,
        DED,
    DED,
    EM,
]
