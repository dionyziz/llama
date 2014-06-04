# ----------------------------------------------------------------------
# parser.py
#
# parser for the Llama language
# http://courses.softlab.ntua.gr/compilers/2012a/llama2012.pdf
#
# Authors: Dimitris Koutsoukos <dimkou@gmail.com>
#          Nick Korasidis <Renelvon@gmail.com>
#          Dionysis Zindros <dionyziz@gmail.com>
# ----------------------------------------------------------------------

from pprint import pprint
import ply.yacc as yacc
from lexer import tokens
import ast, type


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
        p[0] = ast.Program(p[1])

    def p_empty(self, p):
        """empty :"""
        return None

    def p_def_list(self, p):
        """def_list : letdef def_list
                    | typedef def_list
                    | empty"""
        self._expand_list(p)

    def p_typedef(self, p):
        """typedef : TYPE tdef_and_seq"""
        p[0] = ast.TypeDef(p[2])

    def p_tdef(self, p):
        """tdef : GENID EQ constr_pipe_seq"""
        p[0] = ast.TDef(p[3])

    def p_constr_pipe_seq(self, p):
        """constr_pipe_seq : constr
                           | constr PIPE constr_pipe_seq"""
        self._expand_seq(p)

    def p_tdef_and_seq(self, p):
        """tdef_and_seq : tdef
                        | tdef AND tdef_and_seq"""
        self._expand_seq(p)

    def p_constr(self, p):
        """constr : CONID
                  | CONID OF type_seq"""
        p[0] = ast.Constr(p)

    def p_type_seq(self, p):
        """type_seq : type
                    | type type_seq"""
        self._expand_seq(p)

    # Check types during semantic analysis
    def p_type(self, p):
        """type : UNIT
                | INT
                | CHAR
                | BOOL
                | FLOAT
                | paren_type
                | user_type
                | ref_type
                | array_type
                | function_type"""
        if len(p) == 2:
            try:
                p[0] = {
                    'unit': type.Unit(),
                    'int': type.Int(),
                    'char': type.Char(),
                    'bool': type.Bool(),
                    'float': type.Float(),
                }[p[1]]
            except:
                # derived type
                p[0] = p[1]

    def p_paren_type(self, p):
        """paren_type : LPAREN type RPAREN"""
        p[0] = p[2]

    def p_user_type(self, p):
        """user_type : GENID"""
        p[0] = type.User(p[1])

    def p_ref_type(self, p):
        """ref_type : type REF"""
        p[0] = type.Ref(p[1])

    def p_array_type(self, p):
        """array_type : ARRAY OF type
                      | ARRAY LBRACKET star_comma_seq RBRACKET OF type"""
        if len(p) == 4:
            p[0] = type.Array(p[3])
        else:
            p[0] = type.Array(p[6], p[3])

    def p_function_type(self, p):
        """function_type : type ARROW type"""
        p[0] = ast.FunctionType(p[1], p[3])

    def p_star_comma_seq(self, p):
        """star_comma_seq : TIMES
                          | TIMES COMMA star_comma_seq"""
        # count number of dimensions
        if len(p) == 2:
            p[0] = 1
        else:
            p[0] = p[3] + 1

    def p_param(self, p):
        """param : GENID
                 | LPAREN GENID COLON type RPAREN"""
        if len(p) == 6:
            name = p[2]
            type = p[4]
        else:
            name = p[1]
            type = None
        p[0] = ast.Param(name=name, type=type)

    def p_letdef(self, p):
        """letdef : LET def_seq
                  | LET REC def_seq"""
        isRec = len(p) == 4
        p[0] = ast.LetDef(p[-1], isRec)

    def p_def_seq(self, p):
        """def_seq : def
                   | def AND def_seq"""
        self._expand_seq(p)

    def p_def(self, p):
        """def : function_def
               | variable_def"""
        p[0] = p[1]

    def p_function_def(self, p):
        """function_def : GENID param_list EQ expr
                        | GENID param_list COLON type EQ expr"""
        type = None
        if len(p) == 7:
            type = p[5]
        p[0] = ast.FunctionDef(name=p[1], params=p[2], body=p[-1], type=type)

    def p_variable_def(self, p):
        """variable_def : simple_variable_def
                        | array_variable_def"""
        p[0] = p[1]

    def p_simple_variable_def(self, p):
        """simple_variable_def : MUTABLE GENID
                               | MUTABLE GENID COLON type"""
        type = None
        if len(p) == 5:
            type = p[-1]
        p[0] = ast.VariableDef(p[2], type)

    def p_array_variable_def(self, p):
        """array_variable_def : MUTABLE GENID LBRACKET expr_comma_seq RBRACKET
                              | MUTABLE GENID LBRACKET expr_comma_seq RBRACKET COLON type"""
        dataType = None
        if len(p) == 8:
            dataType = p[-1]
        p[0] = ast.VariableDef(p[2], type.Array(refType=dataType, dim=p[4]))

    def p_expr_comma_seq(self, p):
        """expr_comma_seq : expr
                          | expr COMMA expr_comma_seq"""
        self._expand_seq(p)

    def p_simpleexpr_seq(self, p):
        """simpleexpr_seq : simpleexpr
                          | simpleexpr simpleexpr_seq"""
        self._expand_seq(p, 1, 2)

    def p_param_list(self, p):
        """param_list : empty
                      | param param_list"""
        self._expand_list(p)

    def p_simpleexpr(self, p):
        """simpleexpr : iconst_simple_expr
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
    
    def p_iconst_simple_expr(self, p):
        """iconst_simple_expr : ICONST"""

        pprint(p[1])
        # p[0] = ast.SimpleExpression()

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
                | genid_expr
                | conid_expr
                | dim_expr
                | new_expr
                | delete_expr
                | in_expr
                | begin_end_expr
                | if_expr
                | for_expr
                | while_expr
                | match_expr"""
        if len(p) == 2:
            # delegated to other expression / rule
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = ast.UnaryExpression(p[1], p[2])
        elif len(p) == 4:
            p[0] = ast.BinaryExpression(p[2], p[1], p[3])
        else:
            print("Problem")

        # p[0] = [
        #     lambda: p[1],
        #     lambda: if p[1] in UnaryExpression(p[1], p[2])
        #         if p[1] in ['+', '-', 'not']:
        # ][len(p)]

        # # unary operators
        #     p[0] = ast.UnaryExpression(p[1], p[2])
        #     return

        # # binary operators
        # if p[2] in ['+', '-', '*', '/', 'mod', '**', '=', '<>', '==', '!=', '>', '<', '>=', '<=', '&&', '||', ';', ',=']:
        #     p[0] = ast.BinaryExpression(p[1], p[3])
        #     return

    def p_genid_expr(self, p):
        """genid_expr : GENID simpleexpr_seq"""
        pass

    def p_conid_expr(self, p):
        """conid_expr : CONID simpleexpr_seq"""
        pass

    def p_dim_expr(self, p):
        """dim_expr : DIM GENID
                    | DIM ICONST GENID"""
        pass

    def p_new_expr(self, p):
        """new_expr : NEW type"""
        pass

    def p_delete_expr(self, p):
        """delete_expr : DELETE expr"""
        pass

    def p_if_expr(self, p):
        """if_expr : IF expr THEN expr
                   | IF expr THEN expr ELSE expr"""
        pass

    def p_for_expr(self, p):
        """for_expr : FOR GENID EQ expr TO expr DO expr DONE
                    | FOR GENID EQ expr DOWNTO expr DO expr DONE"""
        pass

    def p_while_expr(self, p):
        """while_expr : WHILE expr DO expr DONE"""
        pass

    def p_match_expr(self, p):
        """match_expr : MATCH expr WITH clause_seq END """
        pass

    def p_in_expr(self, p):
        """in_expr : letdef IN expr"""
        pass

    def p_begin_end_expr(self, p):
        """begin_end_expr : BEGIN expr END"""
        pass

    def p_clause_seq(self, p):
        """clause_seq : clause
                      | clause PIPE clause_seq"""
        self._expand_seq(p)

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
        self._expand_list(p)

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

    def _expand_seq(self, p, lastIdx = 1, listIdx = 3):
        if len(p) == lastIdx + 1:
            p[0] = [p[lastIdx]]
        else:
            p[listIdx][0:0] = [p[lastIdx]]
            p[0] = p[listIdx]

    def _expand_list(self, p):
        if p[1] is None:
            # end of list
            p[0] = []
        else:
            p[2][0:0] = [p[1]]
            p[0] = p[2]


    parser = None
    tokens = tokens
    debug = False

    def __init__(self, debug=0):
        self.parser = yacc.yacc(module=self, optimize=0, debug=1)

    def parse(self, lexer, data, debug=0):
        """
        Feed the lexer with the data, then use it to parse
        the input. If debug is enabled, output matched productions
        to stdout.
        """
        self.debug = debug
        self.parser.parse(data, lexer=lexer, debug=debug)
