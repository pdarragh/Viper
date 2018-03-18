from viper.lexer import (
    NEWLINE as NL, INDENT as IND, DEDENT as DED, COLON, OPEN_PAREN as OP, CLOSE_PAREN as CP, ARROW, ENDMARKER as EM,
    Number as Num,
    Name as N,
    Class as C,
    Operator as Op,
)


lexemes = [
    N('def'), N('fib'), OP, N('n'), COLON, C('Int'), CP, ARROW, C('Int'), COLON,
    NL, IND, N('if'), N('n'), Op('=='), Num('1'), N('or'), N('n'), Op('=='), Num('2'), COLON,
    NL, IND, IND, N('return'), Num('1'), DED,
    NL, IND, N('return'), N('fib'), OP, N('n'), Op('-'), Num('1'), CP, Op('+'), N('fib'), OP, N('n'), Op('-'), Num('2'),
    CP, DED,
    NL, EM,
]
