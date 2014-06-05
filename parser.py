# ----------------------------------------------------------------------
# parser.py
#
# parser for the Llama language
# http://courses.softlab.ntua.gr/compilers/2012a/llama2012.pdf
#
# Author: Dimitris Koutsoukos <dimkou.shmmy@gmail.com>
#         Nick Korasidis <Renelvon@gmail.com>
# ----------------------------------------------------------------------

import ply.yacc as yacc
from lexer import tokens


class LlamaParser:
    precedence = (
        # Type operator precedence
        ('right', 'ARROW'),
        ('nonassoc', 'OF'),

        # Normal operator precedence
        ('nonassoc', 'IN'),
        ('left', 'SEMICOLON'),
        ('nonassoc', 'THEN'),
        ('nonassoc', 'ELSE'),
        ('nonassoc', 'ASSIGN'),
        ('left', 'BOR'),
        ('left', 'BAND'),
        ('nonassoc', 'LT', 'LE', 'GT', 'GE', 'EQ', 'NEQ', 'NATEQ', 'NATNEQ'),
        ('left', 'PLUS', 'MINUS', 'FPLUS', 'FMINUS'),
        ('left', 'TIMES', 'DIVIDE', 'FTIMES', 'FDIVIDE', 'MOD'),
        ('right', 'FPOW'),
        ('nonassoc', 'SIGN', 'NOT', 'DELETE')
    )

    # == GRAMMAR RULES ==
    # Naming convention: If A is a non-terminal and B is a separator, then
    #       A_B_list is a potentially empty list of tokens of type A,
    #                separated by tokens of type B.
    #       A_B_seq  is a non-empty list of tokens of type A
    #                separated by tokens of type B.
    # In cases where B is absent, whitespace may be assumed as separator.

    def p_program(self, p):
        """program : def_list"""
        pass

    def p_empty(self, p):
        """empty :"""
        pass

    def p_def_list(self, p):
        """def_list : letdef def_list
                    | typedef def_list
                    | empty"""
        pass

    def p_typedef(self, p):
        """typedef : TYPE tdef_and_seq"""
        pass

    def p_tdef(self, p):
        """tdef : GENID EQ constr_pipe_seq"""
        pass

    def p_constr_pipe_seq(self, p):
        """constr_pipe_seq : constr
                           | constr PIPE constr_pipe_seq"""
        pass

    def p_tdef_and_seq(self, p):
        """tdef_and_seq : tdef
                        | tdef AND tdef_and_seq"""
        pass

    def p_constr(self, p):
        """constr : CONID
                  | CONID OF type_seq"""
        pass

    def p_type_seq(self, p):
        """type_seq : type
                    | type type_seq"""
        pass

    # Check types during semantic analysis
    def p_type(self, p):
        """type : UNIT
                | INT
                | CHAR
                | BOOL
                | FLOAT
                | LPAREN type RPAREN
                | GENID
                | type REF
                | ARRAY OF type
                | ARRAY LBRACKET star_comma_seq RBRACKET OF type
                | type ARROW type"""
        pass

    def p_star_comma_seq(self, p):
        """star_comma_seq : TIMES
                          | TIMES COMMA star_comma_seq"""
        pass

    def p_par(self, p):
        """par : GENID
               | LPAREN GENID COLON type RPAREN"""
        pass

    def p_letdef(self, p):
        """letdef : LET def_seq
                  | LET REC def_seq"""
        pass

    def p_def_seq(self, p):
        """def_seq : def
                   | def AND def_seq"""
        pass

    def p_def(self, p):
        """def : GENID par_list EQ expr
               | GENID par_list COLON type EQ expr
               | MUTABLE GENID
               | MUTABLE GENID COLON type
               | MUTABLE GENID LBRACKET expr_comma_seq RBRACKET
               | MUTABLE GENID LBRACKET expr_comma_seq RBRACKET COLON type"""
        pass

    def p_expr_comma_seq(self, p):
        """expr_comma_seq : expr
                          | expr COMMA expr_comma_seq"""
        pass

    def p_simpleexpr_seq(self, p):
        """simpleexpr_seq : simpleexpr
                          | simpleexpr simpleexpr_seq"""
        pass

    def p_par_list(self, p):
        """par_list : empty
                    | par par_list"""
        pass

    def p_simpleexpr(self, p):
        """simpleexpr : ICONST
                      | FCONST
                      | CCONST
                      | SCONST
                      | TRUE
                      | FALSE
                      | LPAREN RPAREN
                      | BANG simpleexpr
                      | LPAREN expr RPAREN
                      | GENID
                      | CONID
                      | GENID LBRACKET expr_comma_seq RBRACKET"""
        pass

    def p_expr(self, p):
        """expr : simpleexpr
                | PLUS expr %prec SIGN
                | MINUS expr %prec SIGN
                | FPLUS expr %prec SIGN
                | FMINUS expr %prec SIGN
                | NOT expr
                | expr PLUS expr
                | expr MINUS expr
                | expr TIMES expr
                | expr DIVIDE expr
                | expr FPLUS expr
                | expr FMINUS expr
                | expr FTIMES expr
                | expr FDIVIDE expr
                | expr MOD expr
                | expr FPOW expr
                | expr EQ expr
                | expr NEQ expr
                | expr NATEQ expr
                | expr NATNEQ expr
                | expr LT expr
                | expr LE expr
                | expr GT expr
                | expr GE expr
                | expr BOR expr
                | expr BAND expr
                | expr SEMICOLON expr
                | expr ASSIGN expr
                | GENID simpleexpr_seq
                | CONID simpleexpr_seq
                | DIM GENID
                | DIM ICONST GENID
                | NEW type
                | DELETE expr
                | letdef IN expr
                | BEGIN expr END
                | IF expr THEN expr
                | IF expr THEN expr ELSE expr
                | WHILE expr DO expr DONE
                | FOR GENID EQ expr TO expr DO expr DONE
                | FOR GENID EQ expr DOWNTO expr DO expr DONE
                | MATCH expr WITH clause_seq END """
        pass

    def p_clause_seq(self, p):
        """clause_seq : clause
                      | clause PIPE clause_seq"""
        pass

    def p_clause(self, p):
        """clause : pattern ARROW expr"""
        pass

    def p_pattern(self, p):
        """pattern : simplepattern
                   | CONID simplepattern_list"""
        pass

    def p_simplepattern_list(self, p):
        """simplepattern_list : empty
                              | simplepattern simplepattern_list"""
        pass

    def p_simplepattern(self, p):
        """simplepattern : ICONST
                         | PLUS ICONST
                         | MINUS ICONST
                         | FCONST
                         | FPLUS FCONST
                         | FMINUS FCONST
                         | CCONST
                         | TRUE
                         | FALSE
                         | GENID
                         | LPAREN pattern RPAREN"""
        pass

    def p_error(self, p):
        print("Syntax error")

    parser = None
    tokens = tokens
    debug = False

    def __init__(self, debug=0):
        self.parser = yacc.yacc(module=self, optimize=1, debug=debug)

    def parse(self, lexer, data, debug=0):
        """
        Feed the lexer with the data, then use it to parse
        the input. If debug is enabled, output matched productions
        to stdout.
        """
        self.debug = debug
        self.parser.parse(data, lexer=lexer, debug=debug)
