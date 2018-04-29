from viper.lexer import (
    NEWLINE as NL, INDENT as IND, DEDENT as DED, COLON, OPEN_PAREN as OP, CLOSE_PAREN as CP, ARROW, ENDMARKER as EM,
    Number as Num,
    Name as N, ReservedName as RN,
    Class as C,
    Operator as Op,
)


lexemes = [
    RN('def'), N('fib'), OP, N('n'), COLON, C('Int'), CP, ARROW, C('Int'), COLON,
    NL, IND,
        RN('if'), N('n'), Op('=='), Num('1'), RN('or'), N('n'), Op('=='), Num('2'), COLON,
        NL, IND,
            RN('return'), Num('1'), NL,
        DED,
        RN('return'), N('fib'), OP, N('n'), Op('-'), Num('1'), CP, Op('+'), N('fib'), OP, N('n'), Op('-'), Num('2'), CP, NL,
    DED,
    EM,
]
