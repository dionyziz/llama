"""
# ----------------------------------------------------------------------
# parser.py
#
# parser for the Llama language
# http://courses.softlab.ntua.gr/compilers/2012a/llama2012.pdf
#
# Authors: Dimitris Koutsoukos <dim.kou.shmmy@gmail.com>
#          Nick Korasidis <renelvon@gmail.com>
#          Dionysis Zindros <dionyziz@gmail.com>
# ----------------------------------------------------------------------
"""

from ply import yacc

from compiler import ast, error, lex


def _track(p):
    """Add position to root of reduced grammar rule."""
    if isinstance(p[1], ast.Node):
        if p[0] is not p[1]:
            p[0].copy_pos(p[1])
    else:
        node = p[0]
        node.lineno = p.lineno(1)
        node.lexpos = p.lexpos(1)


class Parser:
    """A parser for the Llama language"""
    precedence = (
        # Type operator precedence
        ('right', 'ARROW'),
        ('nonassoc', 'OF'),
        ('nonassoc', 'REF'),

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
        """def_list : letdef def_list
                    | typedef def_list
                    | empty"""
        self._expand_list(p)

    def p_letdef(self, p):
        """letdef : LET REC def_seq
                  | LET def_seq"""
        if len(p) == 4:
            p[0] = ast.LetDef(p[3], isRec=True)
        else:
            p[0] = ast.LetDef(p[2])
        _track(p)

    def p_def_seq(self, p):
        """def_seq : def AND def_seq
                   | def"""
        self._expand_seq(p)

    def p_def(self, p):
        """def : function_def
               | var_def"""
        p[0] = p[1]
        _track(p)

    def p_function_def(self, p):
        """function_def : GENID param_list COLON type EQ expr
                        | GENID param_list EQ expr"""
        if len(p) == 7:
            p[0] = ast.FunctionDef(p[1], p[2], p[6], p[4])
        else:
            p[0] = ast.FunctionDef(p[1], p[2], p[4])
        _track(p)

    def p_param_list(self, p):
        """param_list : param param_list
                      | empty"""
        self._expand_list(p)

    def p_param(self, p):
        """param : LPAREN GENID COLON type RPAREN
                 | GENID"""
        if len(p) == 6:
            p[0] = ast.Param(p[2], p[4])
        else:
            p[0] = ast.Param(p[1])
        _track(p)

    def p_type(self, p):
        """type : LPAREN type RPAREN
                | builtin_type
                | derived_type"""
        if len(p) == 4:
            p[0] = p[2]
        else:
            p[0] = p[1]
        _track(p)

    def p_builtin_type(self, p):
        """builtin_type : BOOL
                        | CHAR
                        | FLOAT
                        | INT
                        | UNIT"""
        p[0] = ast.builtin_types_map[p[1]]()
        _track(p)

    def p_derived_type(self, p):
        """derived_type : array_type
                        | function_type
                        | ref_type
                        | user_type"""
        p[0] = p[1]
        _track(p)

    def p_array_type(self, p):
        """array_type : ARRAY LBRACKET star_comma_seq RBRACKET OF type
                      | ARRAY OF type"""
        if len(p) == 7:
            p[0] = ast.Array(p[6], p[3])
        else:
            p[0] = ast.Array(p[3])
        _track(p)

    def p_star_comma_seq(self, p):
        """star_comma_seq : TIMES COMMA star_comma_seq
                          | TIMES"""
        # We 'll be counting stars :)
        if len(p) == 4:
            p[0] = p[3] + 1
        else:
            p[0] = 1

    def p_function_type(self, p):
        """function_type : type ARROW type"""
        p[0] = ast.Function(p[1], p[3])
        _track(p)

    def p_ref_type(self, p):
        """ref_type : type REF"""
        p[0] = ast.Ref(p[1])
        _track(p)

    def p_user_type(self, p):
        """user_type : GENID"""
        p[0] = ast.User(p[1])
        _track(p)

    def p_empty(self, _):
        """empty :"""
        return None

    def p_expr(self, p):
        """expr : expr PLUS expr
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
                | NOT expr
                | PLUS expr %prec SIGN
                | MINUS expr %prec SIGN
                | FPLUS expr %prec SIGN
                | FMINUS expr %prec SIGN
                | begin_end_expr
                | constructor_call_expr
                | delete_expr
                | dim_expr
                | for_expr
                | function_call_expr
                | in_expr
                | if_expr
                | match_expr
                | simple_expr
                | while_expr"""
        if len(p) == 4:
            p[0] = ast.BinaryExpression(p[1], p[2], p[3])
        elif len(p) == 3:
            p[0] = ast.UnaryExpression(p[1], p[2])
        else:
            p[0] = p[1]
        _track(p)

    def p_begin_end_expr(self, p):
        """begin_end_expr : BEGIN expr END"""
        p[0] = p[2]
        _track(p)

    def p_constructor_call_expr(self, p):
        """constructor_call_expr : CONID simple_expr_seq"""
        p[0] = ast.ConstructorCallExpression(p[1], p[2])
        _track(p)

    def p_simple_expr_seq(self, p):
        """simple_expr_seq : simple_expr simple_expr_seq
                           | simple_expr"""
        self._expand_seq(p, 1, 2)

    def p_simple_expr(self, p):
        """simple_expr : array_simple_expr
                       | paren_simple_expr
                       | bang_simple_expr
                       | new_expr
                       | bconst_simple_expr
                       | cconst_simple_expr
                       | conid_simple_expr
                       | fconst_simple_expr
                       | genid_simple_expr
                       | iconst_simple_expr
                       | sconst_simple_expr
                       | uconst_simple_expr"""
        p[0] = p[1]
        _track(p)

    def p_array_simple_expr(self, p):
        """array_simple_expr : GENID LBRACKET expr_comma_seq RBRACKET"""
        p[0] = ast.ArrayExpression(p[1], p[3])
        _track(p)

    def p_paren_simple_expr(self, p):
        """paren_simple_expr : LPAREN expr RPAREN"""
        p[0] = p[2]
        _track(p)

    def p_bang_simple_expr(self, p):
        """bang_simple_expr : BANG simple_expr"""
        p[0] = ast.UnaryExpression(p[1], p[2])
        _track(p)

    def p_bconst_simple_expr(self, p):
        """bconst_simple_expr : TRUE
                              | FALSE"""
        p[0] = ast.ConstExpression(ast.Bool(), p[1])
        _track(p)

    def p_cconst_simple_expr(self, p):
        """cconst_simple_expr : CCONST"""
        p[0] = ast.ConstExpression(ast.Char(), p[1])
        _track(p)

    def p_conid_simple_expr(self, p):
        """conid_simple_expr : CONID"""
        p[0] = ast.ConidExpression(p[1])
        _track(p)

    def p_iconst_simple_expr(self, p):
        """iconst_simple_expr : ICONST"""
        p[0] = ast.ConstExpression(ast.Int(), p[1])
        _track(p)

    def p_fconst_simple_expr(self, p):
        """fconst_simple_expr : FCONST"""
        p[0] = ast.ConstExpression(ast.Float(), p[1])
        _track(p)

    def p_genid_simple_expr(self, p):
        """genid_simple_expr : GENID"""
        p[0] = ast.GenidExpression(p[1])
        _track(p)

    def p_sconst_simple_expr(self, p):
        """sconst_simple_expr : SCONST"""
        p[0] = ast.ConstExpression(ast.String(), p[1])
        _track(p)

    def p_uconst_simple_expr(self, p):
        """uconst_simple_expr : LPAREN RPAREN"""
        p[0] = ast.ConstExpression(ast.Unit())
        _track(p)

    def p_delete_expr(self, p):
        """delete_expr : DELETE expr"""
        p[0] = ast.DeleteExpression(p[2])
        _track(p)

    def p_dim_expr(self, p):
        """dim_expr : DIM ICONST GENID
                    | DIM GENID"""
        if len(p) == 4:
            p[0] = ast.DimExpression(p[3], p[2])
        else:
            p[0] = ast.DimExpression(p[2])
        _track(p)

    def p_for_expr(self, p):
        """for_expr : for_to_expr
                    | for_downto_expr"""
        p[0] = p[1]
        _track(p)

    def p_for_to_expr(self, p):
        """for_to_expr : FOR GENID EQ expr TO expr DO expr DONE"""
        p[0] = ast.ForExpression(p[2], p[4], p[6], p[8])
        _track(p)

    def p_for_downto_expr(self, p):
        """for_downto_expr : FOR GENID EQ expr DOWNTO expr DO expr DONE"""
        p[0] = ast.ForExpression(p[2], p[4], p[6], p[8], isDown=True)
        _track(p)

    def p_function_call_expr(self, p):
        """function_call_expr : GENID simple_expr_seq"""
        p[0] = ast.FunctionCallExpression(p[1], p[2])
        _track(p)

    def p_in_expr(self, p):
        """in_expr : letdef IN expr"""
        p[0] = ast.LetInExpression(p[1], p[3])
        _track(p)

    def p_if_expr(self, p):
        # WARNING: Changing order of clauses produces Syntax Errors,
        # probably due to a PLY bug.
        """if_expr : IF expr THEN expr
                   | IF expr THEN expr ELSE expr"""
        if len(p) == 7:
            p[0] = ast.IfExpression(p[2], p[4], p[6])
        else:
            p[0] = ast.IfExpression(p[2], p[4])
        _track(p)

    def p_match_expr(self, p):
        """match_expr : MATCH expr WITH clause_seq END"""
        p[0] = ast.MatchExpression(p[2], p[4])
        _track(p)

    def p_clause_seq(self, p):
        """clause_seq : clause PIPE clause_seq
                      | clause"""
        self._expand_seq(p)

    def p_clause(self, p):
        """clause : pattern ARROW expr"""
        p[0] = ast.Clause(p[1], p[3])
        _track(p)

    def p_pattern(self, p):
        """pattern : CONID simple_pattern_list
                   | simple_pattern"""
        if len(p) == 3:
            p[0] = ast.Pattern(p[1], p[2])
        else:
            p[0] = p[1]
        _track(p)

    def p_simple_pattern_list(self, p):
        """simple_pattern_list : simple_pattern simple_pattern_list
                               | empty"""
        self._expand_list(p)

    def p_simple_pattern(self, p):
        """simple_pattern : LPAREN pattern RPAREN
                          | bconst_simple_expr
                          | cconst_simple_expr
                          | fconst_simple_expr
                          | iconst_simple_expr
                          | genid_simple_pattern
                          | mfconst_simple_pattern
                          | miconst_simple_pattern
                          | pfconst_simple_pattern
                          | piconst_simple_pattern"""
        if len(p) == 4:
            p[0] = p[2]
        else:
            p[0] = p[1]
        _track(p)

    def p_genid_simple_pattern(self, p):
        """genid_simple_pattern : GENID"""
        p[0] = ast.GenidPattern(p[1])
        _track(p)

    def p_mfconst_simple_pattern(self, p):
        """mfconst_simple_pattern : FMINUS FCONST"""
        p[0] = ast.ConstExpression(ast.Float(), -p[2])
        _track(p)

    def p_pfconst_simple_pattern(self, p):
        """pfconst_simple_pattern : FPLUS FCONST"""
        p[0] = ast.ConstExpression(ast.Float(), p[2])
        _track(p)

    def p_miconst_simple_pattern(self, p):
        """miconst_simple_pattern : MINUS ICONST"""
        p[0] = ast.ConstExpression(ast.Int(), -p[2])
        _track(p)

    def p_piconst_simple_pattern(self, p):
        """piconst_simple_pattern : PLUS ICONST"""
        p[0] = ast.ConstExpression(ast.Int(), p[2])
        _track(p)

    def p_new_expr(self, p):
        """new_expr : NEW type"""
        p[0] = ast.NewExpression(p[2])
        _track(p)

    def p_while_expr(self, p):
        """while_expr : WHILE expr DO expr DONE"""
        p[0] = ast.WhileExpression(p[2], p[4])
        _track(p)

    def p_var_def(self, p):
        """var_def : array_var_def
                   | simple_var_def"""
        p[0] = p[1]
        _track(p)

    def p_array_var_def(self, p):
        """array_var_def : array_var_def_typed
                         | array_var_def_untyped"""
        p[0] = p[1]
        _track(p)

    def p_array_var_def_typed(self, p):
        """array_var_def_typed : MUTABLE GENID LBRACKET expr_comma_seq RBRACKET COLON type"""
        item_type = p[7]
        arr_type = ast.Array(item_type, len(p[4]))
        p[0] = ast.ArrayVariableDef(p[2], p[4], arr_type)
        _track(p)

    def p_array_var_def_untyped(self, p):
        """array_var_def_untyped : MUTABLE GENID LBRACKET expr_comma_seq RBRACKET"""
        p[0] = ast.ArrayVariableDef(p[2], p[4])
        _track(p)

    def p_expr_comma_seq(self, p):
        """expr_comma_seq : expr COMMA expr_comma_seq
                          | expr"""
        self._expand_seq(p)

    def p_simple_var_def(self, p):
        """simple_var_def : MUTABLE GENID
                          | MUTABLE GENID COLON type"""
        if len(p) == 5:
            vartype = ast.Ref(p[4])
            vartype.copy_pos(p[4])
            p[0] = ast.VariableDef(p[2], vartype)
        else:
            p[0] = ast.VariableDef(p[2])
        _track(p)

    def p_typedef(self, p):
        """typedef : TYPE tdef_and_seq"""
        p[0] = p[2]

    def p_tdef_and_seq(self, p):
        """tdef_and_seq : tdef AND tdef_and_seq
                        | tdef"""
        self._expand_seq(p)

    def p_tdef(self, p):
        """tdef : user_type EQ constr_pipe_seq
                | builtin_type EQ constr_pipe_seq"""
        # NOTE: Flag redefinition of builtin_types during semantic analysis.
        p[0] = ast.TDef(p[1], p[3])
        _track(p)

    def p_constr_pipe_seq(self, p):
        """constr_pipe_seq : constr PIPE constr_pipe_seq
                           | constr"""
        self._expand_seq(p)

    def p_constr(self, p):
        """constr : CONID OF type_seq
                  | CONID"""
        if len(p) == 4:
            p[0] = ast.Constructor(p[1], p[3])
        else:
            p[0] = ast.Constructor(p[1])
        _track(p)

    def p_type_seq(self, p):
        """type_seq : type type_seq
                    | type"""
        self._expand_seq(p, list_idx=2)

    def p_error(self, p):
        """Signal syntax error"""
        if p is not None:
            self.logger.error(
                "%d:%d: error: Syntax error on token %s\t%s",
                p.lineno,
                p.lexpos,
                p.type,
                p.value
            )
        else:
            self.logger.error("Syntax error in unknown token")

    def _expand_seq(self, p, last_idx=1, list_idx=3):
        if len(p) == last_idx + 1:
            p[0] = [p[last_idx]]
        else:
            p[list_idx].insert(0, p[last_idx])
            p[0] = p[list_idx]

    def _expand_list(self, p):
        if p[1] is None:
            # end of list
            p[0] = []
        else:
            p[2].insert(0, p[1])
            p[0] = p[2]

    parser = None
    tokens = lex.tokens
    logger = None
    verbose = False

    def __init__(self, debug=False, logger=None, optimize=True,
                 start='program', verbose=False):
        """
        Create a parser.

        By default, the parser is optimized (i.e. caches LALR tables
        accross invocations).
        If a 'logger' is not provided, create one.
        For detailed reporting on the tables construction, enable
        'debug' and check the 'parser.out' file.
        For manually specifying the initial state, modify 'start'.
        For echoing LR stack to stdout while parsing, enable 'verbose'.
        """
        self.verbose = verbose
        if logger is None:
            self.logger = error.Logger()
        else:
            self.logger = logger

        if start == 'program':
            errorlog = None
            yaccfile = 'parsetab'
        else:
            # Explicitly silence warnings about unused rules when
            # starting from a state other than the default. In addition,
            # send parser cache to a special file, to avoid conflicts and
            # make cleaning easy
            errorlog = yacc.NullLogger()
            yaccfile = "%s_%s" % ('aux', start)

        self.parser = yacc.yacc(
            module=self,
            errorlog=errorlog,
            debug=debug,
            optimize=optimize,
            start=start,
            tabmodule=yaccfile
        )

        if verbose:
            self.logger.info(
                "%s: %s: %s",
                __name__,
                self.__class__.__name__,
                'parser ready'
            )

    def parse(self, data, lexer=None):
        """
        Parse the input and return the AST. If a lexer is not provided,
        create one on the fly.
        """
        if lexer is None:
            lexer = lex.Lexer(logger=self.logger)
        return self.parser.parse(data, lexer, debug=self.verbose)


def parse(data, start='program', logger=None):
    """
    Parse the given string using the default Parser. Return the AST.
    For parsing using a specific subgrammar, set 'start' appropriately.
    For customised error reporting, provide a 'logger'.
    """
    parser = Parser(logger=logger, start=start)
    return parser.parse(data)
