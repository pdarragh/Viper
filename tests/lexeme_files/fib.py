from viper.lexer import (
    NEWLINE, INDENT,
    Number as Num,
    Name as N,
    Class as C,
    Operator as Op,
)


lexemes = [
    N('def'), N('fib'), Op('('), N('n'), Op(':'), C('Int'), Op(')'), Op('->'), C('Int'), Op(':'), NEWLINE,
    INDENT, N('if'), N('n'), Op('=='), Num('1'), N('or'), N('n'), Op('=='), Num('2'), Op(':'), NEWLINE,
    INDENT, INDENT, N('return'), Num('1'), NEWLINE,
    INDENT, N('return'), N('fib'), Op('('), N('n'), Op('-'), Num('1'), Op(')'), Op('+'), N('fib'), Op('('), N('n'),
    Op('-'), Num('2'), Op(')'), NEWLINE
]
