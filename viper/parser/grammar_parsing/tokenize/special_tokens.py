import viper.lexer as vl

from .grammar_token import GrammarToken


INDENT = GrammarToken(vl.Indent)
DEDENT = GrammarToken(vl.Dedent)
ENDMARKER = GrammarToken(vl.EndMarker)
NEWLINE = GrammarToken(vl.NewLine)
PERIOD = GrammarToken(vl.Period, vl.PERIOD.text)
EQUALS = GrammarToken(vl.Equals, vl.EQUALS.text)
COMMA = GrammarToken(vl.Comma, vl.COMMA.text)
OPEN_PAREN = GrammarToken(vl.OpenParen, vl.OPEN_PAREN.text)
CLOSE_PAREN = GrammarToken(vl.CloseParen, vl.CLOSE_PAREN.text)
COLON = GrammarToken(vl.Colon, vl.COLON.text)
L_ARROW = GrammarToken(vl.LeftArrow, vl.L_ARROW.text)
R_ARROW = GrammarToken(vl.RightArrow, vl.R_ARROW.text)
ELLIPSIS = GrammarToken(vl.Ellipsis, vl.ELLIPSIS.text)
INT = GrammarToken(vl.Int)
FLOAT = GrammarToken(vl.Float)
STRING = GrammarToken(vl.String)
NAME = GrammarToken(vl.Name)
UNDERSCORE = GrammarToken(vl.Underscore)
CLASS = GrammarToken(vl.Class)
OPERATOR = GrammarToken(vl.Operator)


SPECIAL_TOKENS = {
    'INDENT':      INDENT,
    'DEDENT':      DEDENT,
    'ENDMARKER':   ENDMARKER,
    'NEWLINE':     NEWLINE,
    'PERIOD':      PERIOD,
    '.':           PERIOD,
    'ASSIGN':      EQUALS,
    '=':           EQUALS,
    'COMMA':       COMMA,
    ',':           COMMA,
    'OPEN_PAREN':  OPEN_PAREN,
    '(':           OPEN_PAREN,
    'CLOSE_PAREN': CLOSE_PAREN,
    ')':           CLOSE_PAREN,
    'COLON':       COLON,
    ':':           COLON,
    'L_ARROW':     L_ARROW,
    '<-':          L_ARROW,
    'R_ARROW':     R_ARROW,
    '->':          R_ARROW,
    'ELLIPSIS':    ELLIPSIS,
    '...':         ELLIPSIS,
    'INT':         INT,
    'FLOAT':       FLOAT,
    'STRING':      STRING,
    'NAME':        NAME,
    'UNDERSCORE':  UNDERSCORE,
    '_':           UNDERSCORE,
    'CLASS':       CLASS,
    'OPERATOR':    OPERATOR,
}
