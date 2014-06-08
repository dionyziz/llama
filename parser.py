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

import ply.yacc as yacc

from lexer import tokens
import ast
import type


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

    def p_def_list(self, p):
        """def_list : empty
                    | typedef def_list
                    | letdef def_list"""
        self._expand_list(p)

    def p_empty(self, p):
        """empty :"""
        return []

    def p_typedef(self, p):
        """typedef : TYPE tdef_and_seq"""
        p[0] = ast.TypeDef(p[2])

    def p_tdef_and_seq(self, p):
        """tdef_and_seq : tdef
                        | tdef AND tdef_and_seq"""
        self._expand_seq(p)

    def p_tdef(self, p):
        """tdef : GENID EQ constr_pipe_seq"""
        p[0] = ast.TDef(p[1], p[3])

    def p_constr_pipe_seq(self, p):
        """constr_pipe_seq : constr
                           | constr PIPE constr_pipe_seq"""
        self._expand_seq(p)

    def p_constr(self, p):
        """constr : CONID
                  | CONID OF type_seq"""
        typeSeq = None
        if len(p) == 4:
            typeSeq = p[3]
        p[0] = ast.Constr(p[1], typeSeq)

    def p_type_seq(self, p):
        """type_seq : type
                    | type type_seq"""
        self._expand_seq(p, listIdx=2)

    def p_type(self, p):
        """type : base_type
                | derived_type
                | LPAREN type RPAREN"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[2]

    _base_type_map = {
        'bool': type.Bool,
        'char': type.Char,
        'float': type.Float,
        'int': type.Int,
        'unit': type.Unit
    }

    def p_base_type(self, p):
        """base_type : BOOL
                     | CHAR
                     | FLOAT
                     | INT
                     | UNIT"""
        p[0] = self._base_type_map[p[1]]()

    def p_derived_type(self, p):
        """derived_type : array_type
                        | function_type
                        | ref_type
                        | user_type"""
        p[0] = p[1]

    def p_array_type(self, p):
        """array_type : ARRAY OF type
                      | ARRAY LBRACKET star_comma_seq RBRACKET OF type"""
        if len(p) == 4:
            p[0] = type.Array(p[3])
        else:
            p[0] = type.Array(p[6], p[3])

    def p_star_comma_seq(self, p):
        """star_comma_seq : TIMES
                          | TIMES COMMA star_comma_seq"""
        # We 'll be counting stars :)
        if len(p) == 2:
            p[0] = 1
        else:
            p[0] = p[3] + 1

    def p_function_type(self, p):
        """function_type : type ARROW type"""
        p[0] = type.Function(p[1], p[3])

    def p_ref_type(self, p):
        """ref_type : type REF"""
        p[0] = type.Ref(p[1])

    def p_user_type(self, p):
        """user_type : GENID"""
        p[0] = type.User(p[1])

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
        if len(p) == 4:
            isRec = True
            ddef = p[3]
        else:
            isRec = False
            ddef = p[2]
        p[0] = ast.LetDef(ddef, isRec=isRec)

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
        if len(p) == 7:
            type = p[4]
            body = p[6]
        else:
            type = None
            body = p[4]
        p[0] = ast.FunctionDef(name=p[1], params=p[2], body=body, type=type)

    def p_variable_def(self, p):
        """variable_def : simple_variable_def
                        | array_variable_def"""
        p[0] = p[1]

    def p_simple_variable_def(self, p):
        """simple_variable_def : MUTABLE GENID
                               | MUTABLE GENID COLON type"""
        type = None
        if len(p) == 5:
            type = p[4]
        p[0] = ast.VariableDef(p[2], type)

    def p_array_variable_def(self, p):
        """array_variable_def : MUTABLE GENID LBRACKET expr_comma_seq RBRACKET
                              | MUTABLE GENID LBRACKET expr_comma_seq RBRACKET COLON type"""
        dataType = None
        if len(p) == 8:
            dataType = p[7]
        p[0] = ast.ArrayVariableDef(p[2], dataType, p[4])

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
                      | fconst_simple_expr
                      | cconst_simple_expr
                      | sconst_simple_expr
                      | bconst_simple_expr
                      | uconst_simple_expr
                      | genid_simple_expr
                      | conid_simple_expr
                      | BANG simpleexpr
                      | LPAREN expr RPAREN
                      | GENID LBRACKET expr_comma_seq RBRACKET"""
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = ast.BangExpression(p[2])
        elif len(p) == 4:
            p[0] = p[2]
        elif len(p) == 5:
            p[0] = ast.ArrayExpression(p[1], p[3])

    def p_iconst_simple_expr(self, p):
        """iconst_simple_expr : ICONST"""
        p[0] = ast.IconstExpression(p[1])

    def p_fconst_simple_expr(self, p):
        """fconst_simple_expr : FCONST"""
        p[0] = ast.FconstExpression(p[1])

    def p_cconst_simple_expr(self, p):
        """cconst_simple_expr : CCONST"""
        p[0] = ast.CconstExpression(value=p[1])

    def p_sconst_simple_expr(self, p):
        """sconst_simple_expr : SCONST"""
        p[0] = ast.SconstExpression(p[1])

    def p_bconst_simple_expr(self, p):
        """bconst_simple_expr : TRUE
                              | FALSE"""
        p[0] = ast.BconstExpression(p[1])

    def p_uconst_simple_expr(self, p):
        """uconst_simple_expr : LPAREN RPAREN"""
        p[0] = ast.UconstExpression()

    def p_genid_simple_expr(self, p):
        """genid_simple_expr : GENID"""
        p[0] = ast.GenidExpression(p[1])

    def p_conid_simple_expr(self, p):
        """conid_simple_expr : CONID"""
        p[0] = ast.ConidExpression(p[1])

    def p_expr(self, p):
        """expr : simpleexpr
                | gcall_expr
                | ccall_expr
                | dim_expr
                | new_expr
                | delete_expr
                | in_expr
                | begin_end_expr
                | if_expr
                | for_expr
                | while_expr
                | match_expr
                | NOT expr
                | PLUS expr %prec SIGN
                | MINUS expr %prec SIGN
                | FPLUS expr %prec SIGN
                | FMINUS expr %prec SIGN
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
                | expr ASSIGN expr"""
        if len(p) == 2:
            # delegated to other expression / rule
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = ast.UnaryExpression(p[1], p[2])
        else:
            p[0] = ast.BinaryExpression(p[2], p[1], p[3])

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

    def p_gcall_expr(self, p):
        """gcall_expr : GENID simpleexpr_seq"""
        p[0] = ast.GcallExpression(p[1], p[2])

    def p_ccall_expr(self, p):
        """ccall_expr : CONID simpleexpr_seq"""
        p[0] = ast.CcallExpression(p[1], p[2])

    def p_dim_expr(self, p):
        """dim_expr : DIM GENID
                    | DIM ICONST GENID"""
        if len(p) == 3:
            dim = 0
            name = p[2]
        else:
            dim = p[1]
            name = p[3]
        p[0] = ast.DimExpression(name, dim)

    def p_new_expr(self, p):
        """new_expr : NEW type"""
        p[0] = ast.NewExpression(p[2])

    def p_delete_expr(self, p):
        """delete_expr : DELETE expr"""
        p[0] = ast.DeleteExpression(p[2])

    def p_if_expr(self, p):
        """if_expr : IF expr THEN expr
                   | IF expr THEN expr ELSE expr"""
        if len(p) == 5:
            elseExpr = None
        else:
            elseExpr = p[6]
        p[0] = ast.IfExpression(p[2], p[4], elseExpr)

    def p_for_expr(self, p):
        """for_expr : FOR GENID EQ expr TO expr DO expr DONE
                    | FOR GENID EQ expr DOWNTO expr DO expr DONE"""
        if p[5] == 'TO':
            p[0] = ast.ForExpression(p[2], p[4], p[6], p[8])
        else:
            p[0] = ast.ForExpression(p[2], p[4], p[6], p[8], downFlag=True)

    def p_while_expr(self, p):
        """while_expr : WHILE expr DO expr DONE"""
        p[0] = ast.WhileExpression(p[2], p[4])

    def p_match_expr(self, p):
        """match_expr : MATCH expr WITH clause_seq END """
        p[0] = ast.MatchExpression(p[2], p[4])

    def p_in_expr(self, p):
        """in_expr : letdef IN expr"""
        p[0] = ast.LetInExpression(p[1], p[3])

    def p_begin_end_expr(self, p):
        """begin_end_expr : BEGIN expr END"""
        p[0] = p[2]

    def p_clause_seq(self, p):
        """clause_seq : clause
                      | clause PIPE clause_seq"""
        self._expand_seq(p)

    def p_clause(self, p):
        """clause : pattern ARROW expr"""
        p[0] = ast.Clause(p[1], p[3])

    def p_pattern(self, p):
        """pattern : simplepattern
                   | CONID simplepattern_list"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.Pattern(p[1], p[2])

    def p_simplepattern_list(self, p):
        """simplepattern_list : empty
                              | simplepattern simplepattern_list"""
        self._expand_list(p)

    def p_simplepattern(self, p):
        """simplepattern : iconst_simple_pattern
                         | miconst_simple_pattern
                         | fconst_simple_pattern
                         | mfconst_simple_pattern
                         | cconst_simple_pattern
                         | bconst_simple_pattern
                         | genid_simple_pattern
                         | LPAREN pattern RPAREN"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[2]

    def p_iconst_simple_pattern(self, p):
        """iconst_simple_pattern : ICONST
                                 | PLUS ICONST"""
        if len(p) == 2:
            p[0] = ast.IconstPattern(p[1])
        else:
            p[0] = ast.IconstPattern(p[2])

    def p_miconst_simple_pattern(self, p):
        """miconst_simple_pattern : MINUS ICONST"""
        p[0] = ast.IconstPattern(-p[2])

    def p_fconst_simple_pattern(self, p):
        """fconst_simple_pattern : FCONST
                                 | FPLUS FCONST"""
        if len(p) == 2:
            p[0] = ast.FconstPattern(p[1])
        else:
            p[0] = ast.FconstPattern(p[2])

    def p_mfconst_simple_pattern(self, p):
        """mfconst_simple_pattern : FMINUS FCONST"""
        p[0] = ast.FconstPattern(-p[2])

    def p_cconst_simple_pattern(self, p):
        """cconst_simple_pattern : CCONST"""
        p[0] = ast.CconstPattern(p[1])

    def p_bconst_simple_pattern(self, p):
        """bconst_simple_pattern : TRUE
                                 | FALSE"""
        p[0] = ast.BconstPattern(p[1])

    def p_genid_simple_pattern(self, p):
        """genid_simple_pattern : GENID"""
        p[0] = ast.GenidPattern(p[1])

    def p_error(self, p):
        print("Syntax error")

    def _expand_seq(self, p, lastIdx=1, listIdx=3):
        if len(p) == lastIdx + 1:
            p[0] = [p[lastIdx]]
        else:
            p[listIdx].insert(0, p[lastIdx])
            p[0] = p[listIdx]

    def _expand_list(self, p):
        if p[1] is None:
            # end of list
            p[0] = []
        else:
            p[2].insert(0, p[1])
            p[0] = p[2]

    parser = None
    tokens = tokens
    debug = False

    def __init__(self, debug=0):
        self.parser = yacc.yacc(module=self, optimize=1, debug=1)

    def parse(self, lexer, data, debug=0):
        """
        Feed the lexer with the data, then use it to parse
        the input. If debug is enabled, output matched productions
        to stdout.
        """
        self.debug = debug
        self.parser.parse(data, lexer=lexer, debug=debug)
