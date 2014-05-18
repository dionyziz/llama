import ply.yacc as yacc
from lexer import tokens

class LlamaParser :
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

    def p_program(self, p) :
        'program  : deflist EOF'
        pass
    
    def p_empty(self, p) :
        'empty : '
        pass
    
    def p_deflist(self, p) :
        '''deflist : letdef deflist
           | typedef deflist
                   | empty'''
        pass
    
    def p_typedef(self, p) :
        'typedef : TYPE tdefandseq'
        pass
    
    def p_tdef(self, p) :
        'tdef : GENID EQ constructorseq'
        pass
    
    def p_constructorseq(self, p) :
        '''constructorseq : constr 
              | constr PIPE constructorseq'''
        pass
    
    def p_tdefandseq(self, p) :
        '''tdefandseq : tdef 
              | tdef AND tdefandseq'''
        pass
    
    def p_constr(self, p) :
        '''constr : CONID 
          | CONID OF typeseq'''
        pass
    
    def p_typeseq(self, p) :
        '''typeseq : type 
         | type typeseq'''
        pass
    
    # Check types during semantic analysis
    def p_type(self, p) :
        '''type : UNIT 
                | INT 
                | CHAR 
                | BOOL 
                | FLOAT 
                | LPAREN type RPAREN 
                | GENID
                | type REF 
                | ARRAY OF type 
                | ARRAY LBRACKET starseq RBRACKET OF type
                | type ARROW type'''
        pass

    def p_starseq(self, p) :
        '''starseq : TIMES 
         | TIMES COMMA starseq'''
        pass
    
    def p_par(self, p) :
        '''par : GENID 
           | LPAREN GENID COLON type RPAREN'''
        pass
    
    def p_letdef(self, p) :
        '''letdef : LET defseq 
        | LET REC defseq'''
        pass
    
    def p_defseq(self, p) :
        '''defseq : def 
        | def AND defseq'''
        pass
    
    def p_def(self, p) :
        '''def : GENID parlist EQ expr 
           | GENID parlist COLON type EQ expr
           | MUTABLE GENID 
           | MUTABLE GENID COLON type 
           | MUTABLE GENID LBRACKET expr_comma_seq RBRACKET
           | MUTABLE GENID LBRACKET expr_comma_seq RBRACKET COLON type'''
        pass
    
    def p_expr_comma_seq(self, p) :
        '''expr_comma_seq : expr 
           | expr COMMA expr_comma_seq'''
        pass
    
    def p_simple_expr_seq(self, p) :
        '''simple_expr_seq : simpleexpr
                           | simpleexpr simple_expr_seq'''
        pass
    
    def p_parlist(self, p) :
        '''parlist : empty 
           | par parlist'''
        pass

    def p_simpleexpr(self, p):
        '''simpleexpr : ICONST 
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
        | GENID LBRACKET expr_comma_seq RBRACKET'''
        pass

    def p_expr(self, p) :
        '''expr : simpleexpr
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
        | GENID simple_expr_seq
        | CONID simple_expr_seq
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
        | MATCH expr WITH clauseseq END '''
        pass
    
    def p_clauseseq(self, p) :
        '''clauseseq : clause 
             | clause PIPE clauseseq'''
        pass
    
    def p_clause(self, p) :
        '''clause : pattern ARROW expr'''
        pass
    
    def p_pattern(self, p) :
        '''pattern : simple_pattern
                   | CONID simple_patternlist'''
        pass
    
    def p_simple_patternlist(self, p) :
        '''simple_patternlist : empty 
               | simple_pattern simple_patternlist'''
        pass

    def p_simple_pattern(self, p) :
        '''simple_pattern : ICONST 
           | PLUS ICONST 
           | MINUS ICONST 
           | FCONST 
           | FPLUS FCONST 
           | FMINUS FCONST
           | CCONST 
           | TRUE 
           | FALSE 
           | GENID 
           | LPAREN pattern RPAREN '''
        pass

    parser = None
    tokens = tokens
    debug = False
    input_file = None
    data = None

    def __init__(self, debug=0) :
        self.parser = yacc.yacc(module=self, optimize=1, debug=debug)

    def p_error(self, p):
        print("Syntax error")

    def parse(self, lexer, data=None, input_file=None, debug=1):
        '''Feed the parser with input.'''
        if not data :
            if input_file :
                try :
                    fd = open(input_file)
                    data = fd.read()
                    fd.close()
                except IOError as e :
                    sys.exit(
                        'Could not open file %s for reading. Aborting.'
                        % input_file
                    )
            else :
                self.input_file = '<stdin>'
                # FIXME : Choose an appropriate output stream
                sys.stdout.write(
                    "Reading from standard input (type <EOF> to end) :"
                )
                sys.stdout.flush()
                data = sys.stdin.read()
        self.data = data
        self.input_file = input_file
        self.debug = debug
        self.parser.parse(data, lexer=lexer, debug=debug)
