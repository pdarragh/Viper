from viper.lexer import (
    NEWLINE, INDENT, COLON, OPEN_PAREN as OP, CLOSE_PAREN as CP, ARROW,
    Number as Num,
    Name as N,
    Class as C,
    Operator as Op,
)


lexemes = [
    N('def'), N('fib'), OP, N('n'), COLON, C('Int'), CP, ARROW, C('Int'), COLON, NEWLINE,
    INDENT, N('if'), N('n'), Op('=='), Num('1'), N('or'), N('n'), Op('=='), Num('2'), COLON, NEWLINE,
    INDENT, INDENT, N('return'), Num('1'), NEWLINE,
    INDENT, N('return'), N('fib'), OP, N('n'), Op('-'), Num('1'), CP, Op('+'), N('fib'), OP, N('n'), Op('-'), Num('2'),
    CP, NEWLINE
]
