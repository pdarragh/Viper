from viper.lexer import (
    NEWLINE, INDENT,
    Name as N,
    Class as C,
    Operator as Op,
)


lexemes = [
    N('data'), C('Tree'), Op('('), N('a'), Op(')'), Op(':'), NEWLINE,
    INDENT, C('Leaf'), N('a'), NEWLINE,
    INDENT, C('Branch'), Op('('), C('Tree'), N('a'), Op(')'), Op('('), C('Tree'), N('a'), Op(')'), NEWLINE
]
