from viper.lexer import (
    NEWLINE as NL, INDENT as IND, DEDENT as DED, COLON as COL, OPEN_PAREN as OP, CLOSE_PAREN as CP, ENDMARKER as EM,
    ARROW as ARR,
    Number as Num,
    Name as N, ReservedName as RN,
    Class as C,
    Operator as Op,
)

lexemes = [
    RN('def'), N('func'), OP, N('y'), COL, C('Int'), CP, ARR, C('Int'), COL,
    NL, IND,
        N('x'), Op('='), Num('0'), NL,
        RN('if'), N('y'), Op('=='), Num('2'), RN('or'), N('y'), Op('>'), Num('9'), COL,
        NL, IND,
            N('x'), Op('='), Num('19'), NL,
            N('x'), Op('+='), N('y'), NL,
        DED,
        RN('else'), COL,
        NL, IND,
            RN('if'), N('y'), Op('%'), Num('3'), Op('=='), Num('0'), COL,
            NL, IND,
                N('x'), Op('='), Num('2'), NL,
                N('x'), Op('*='), N('y'), NL,
            DED,
        DED,
        RN('return'), N('x'), Op('+'), N('y'), NL,
    DED,
    EM,
]