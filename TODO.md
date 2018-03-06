# Viper To-Do List


## Lexer

- Produce keyword lexemes (instead of relying on the parser to handle this)
  - Produce a generic "Keyword" class analogous to "Name"
  - Generate list of keywords from formal grammar


## Parser

- Convert ParseTree to meaningful AST


## Grammar

- Ensure that when defining an operator, there is a way to specify associativity (left, right, none) and precedence
- Look at Perl-6 operators
- Finalize grammar


## General

- Document types and interesting methods
- Convert interactive viper.py to use subcommands
- Determine whether to switch to brace-style (instead of Python-like indentation style)
