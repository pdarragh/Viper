import viper.lexer as vl

from .grammar_token import GrammarToken


INDENT = GrammarToken(vl.Indent)
DEDENT = GrammarToken(vl.Dedent)
ENDMARKER = GrammarToken(vl.EndMarker)
NEWLINE = GrammarToken(vl.NewLine)
PERIOD = GrammarToken(vl.Period, vl.PERIOD.text)
COMMA = GrammarToken(vl.Comma, vl.COMMA.text)
OPEN_PAREN = GrammarToken(vl.OpenParen, vl.OPEN_PAREN.text)
CLOSE_PAREN = GrammarToken(vl.CloseParen, vl.CLOSE_PAREN.text)
COLON = GrammarToken(vl.Colon, vl.COLON.text)
L_ARROW = GrammarToken(vl.LeftArrow, vl.L_ARROW.text)
R_ARROW = GrammarToken(vl.RightArrow, vl.R_ARROW.text)
ELLIPSIS = GrammarToken(vl.Ellipsis, vl.ELLIPSIS.text)
NUMBER = GrammarToken(vl.Number)
NAME = GrammarToken(vl.Name)
CLASS = GrammarToken(vl.Class)
OPERATOR = GrammarToken(vl.Operator)


SPECIAL_TOKENS = {
    'INDENT':      INDENT,
    'DEDENT':      DEDENT,
    'ENDMARKER':   ENDMARKER,
    'NEWLINE':     NEWLINE,
    'PERIOD':      PERIOD,
    '.':           PERIOD,
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
    'NUMBER':      NUMBER,
    'NAME':        NAME,
    'CLASS':       CLASS,
    'OPERATOR':    OPERATOR,
}
