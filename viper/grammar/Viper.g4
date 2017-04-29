grammar Viper;

tokens { NAME
       , NEWLINE
       , INDENT
       , DEDENT
       , NUMBER
       , STRING
       }

func_def: 'def' func_name parameters '->' func_type ':' suite ;
func_name: NAME ;
func_type: type_expr ;

parameters: '(' params_list? ')' ;
params_list: argless_parameter parameter* ;
parameter: arg_label? argless_parameter ;
argless_parameter: param_name ':' param_type ;
arg_label: NAME ;
param_name: NAME ;
param_type: type_expr ;

type_expr: NAME ;

suite: ( simple_stmt
       | NEWLINE INDENT stmt+ DEDENT
       ) ;

stmt: ( simple_stmt
      | compound_stmt
      ) ;

simple_stmt: expr_stmt NEWLINE ;
expr_stmt: ( expr_list
           | 'pass'
           | 'return' expr_list?
           ) ;

expr_list: expr (',' expr)* ;

expr: atom_expr ;
atom_expr: atom trailer* ;
atom: ( '(' expr_list? ')'
      | NAME
      | NUMBER
      | STRING
      | '...'
      | 'Zilch'
      | 'True'
      | 'False'
      ) ;
trailer: ( '(' arg_list? ')'
         | '.' NAME
         ) ;

compound_stmt: ( func_def
               | object_def
               | data_def
               ) ;

object_def: ( class_def
            | interface_def
            | implementation_def
            ) ;

class_def: 'class' common_def ;
interface_def: 'interface' common_def ;
implementation_def: NAME common_def ;
data_def: 'data' common_def ;
common_def: NAME ('(' arg_list? ')')? ':' suite ;
arg_list: argument (',' argument)* ;
argument: expr ;
