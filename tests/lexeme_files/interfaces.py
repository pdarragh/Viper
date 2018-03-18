from viper.lexer import (
    NEWLINE as NL, INDENT as IND, DEDENT as DED, PERIOD, COMMA, COLON, OPEN_PAREN as OP, CLOSE_PAREN as CP, ARROW,
    ENDMARKER as EM,
    Number as Num,
    Name as N, ReservedName as RN,
    Class as C,
    Operator as Op,
)


lexemes = [
    RN('interface'), C('Shape'), COLON,
    NL, IND,
        RN('def'), N('get_area'), OP, CP, ARROW, C('Float'), NL,
     DED,
    C('Shape'), C('Circle'), COLON,
    NL, IND,
        RN('def'), N('init'), OP, N('radius'), COLON, C('Int'), CP, COLON,
        NL, IND,
            N('self'), PERIOD, N('radius'), COLON, C('Int'), Op('='), N('radius'), NL,
        DED,
        RN('def'), N('get_area'), OP, CP, ARROW, C('Float'), COLON,
        NL, IND,
            RN('return'), N('pi'), Op('*'), OP, N('self'), PERIOD, N('radius'), Op('^'), Num('2'), CP, NL,
        DED,
    DED,
    C('Shape'), C('Quadrilateral'), COLON,
    NL, IND,
        RN('def'), N('init'), OP, N('length'), COLON, C('Int'), COMMA, N('width'), COLON, C('Int'), CP, COLON,
        NL, IND,
            N('self'), PERIOD, N('length'), COLON, C('Int'), Op('='), N('length'), NL,
            N('self'), PERIOD, N('width'), COLON, C('Int'), Op('='), N('width'), NL,
        DED,
        RN('def'), N('get_area'), OP, CP, ARROW, C('Float'), COLON,
        NL, IND,
            RN('return'), N('self'), PERIOD, N('length'), Op('*'), N('self'), PERIOD, N('width'), NL,
        DED,
    DED,
    C('Quadrilateral'), C('Rectangle'), COLON,
    NL, IND,
        RN('pass'), NL,
    DED,
    C('Quadrilateral'), C('Square'), COLON,
    NL, IND,
        RN('def'), N('init'), OP, N('side'), COLON, C('Int'), CP, COLON,
        NL, IND,
            N('self'), PERIOD, N('length'), COLON, C('Int'), Op('='), N('side'), NL,
            N('self'), PERIOD, N('width'), COLON, C('Int'), Op('='), N('side'), NL,
        DED,
    DED,
    EM,
]
