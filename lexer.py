# ----------------------------------------------------------------------
# lexer.py
#
# Lexer for the Llama language
# http://courses.softlab.ntua.gr/compilers/2012a/llama2012.pdf
#
# Author: Nick Korasidis <Renelvon@gmail.com>
#
# Lexer design is heavily inspired from the PHPLY lexer
# https://github.com/ramen/phply/blob/master/phply/phplex.py
# ----------------------------------------------------------------------

import re
import sys

import ply.lex as lex

# Represent reserved words as a frozenset for fast lookup
_reserved_words = frozenset('''
    and
    array
    begin
    bool
    char
    delete
    dim
    do
    done
    downto
    else
    end
    false
    float
    for
    if
    in
    int
    let
    match
    mod
    mutable
    new
    not
    of
    rec
    ref
    then
    to
    true
    type
    unit
    while
    with
    '''.split()
)

_reserved_tokens = tuple(s.upper() for s in _reserved_words)

_other_tokens = (
    # Identifiers (generic variable identifiers, constructor identifiers)
    'GENID', 'CONID',

    # Literals (int constant, float constant, char constant, string const)
    'ICONST', 'FCONST', 'CCONST', 'SCONST',

    # Integer operators (+, -, *, /)
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',

    # Floating-point operators (+., -., *., /., **)
    'FPLUS', 'FMINUS', 'FTIMES', 'FDIVIDE', 'FPOW',

    # Boolean operators (&&, ||)
    'BAND', 'BOR',

    # Comparison operators (<, <=, >, >=, =, <>, ==, !=)
    'LT', 'LE', 'GT', 'GE', 'EQ', 'NEQ', 'NATEQ', 'NATNEQ',

    # Pattern operators (->, |)
    'ARROW', 'PIPE',

    # Assignment and dereference (:=, !)
    'ASSIGN', 'BANG',

    # Semicolon (;)
    'SEMICOLON',

    # Delimeters ( ) [ ] , :
    'LPAREN', 'RPAREN',
    'LBRACKET', 'RBRACKET',
    'COMMA', 'COLON'
)

# All valid_tokens [exported]
tokens = _reserved_tokens + _other_tokens


class LlamaLexer:
    """An instrumented llama lexer"""

    # Token list needed by PLY
    tokens = tokens

    # Lexer states
    states = (
        ('comment', 'exclusive'),
        ('char',    'exclusive'),
        ('string',  'exclusive')
    )

    # Has any error happend during lexing?
    error = False

    # Input info
    input_file = 'dummy'  # Deprecated. Will be removed in next version.
    data = None

    # The inner lexer, as constructed by PLY
    lexer = None

    # If debug is True, token will be duplicated to stdout.
    debug = False

    # Index of the most recent beginning of line
    bol = 0

    # Levels of nested comment blocks still open
    level = 0

    # MAXINT
    # TODO: Is this the right place for this?
    max_uint = 2**32 - 1

    def __init__(self, debug=False):
        """
        Initialize wrapper object of PLY lexer. To get a working LlamaLexer,
        invoke build() on the returned object.
        """
        self.debug = debug

    # == ERROR PROCESSING ==

    # TODO: Make error style more gcc-like
    def error_out(self, message, lineno=None, lexpos=None):
        """Signal lexing error."""
        self.error = True
        if lineno is not None:
            if lexpos is not None:
                s = "%s: %d:%d Error: %s" % (
                    self.input_file, lineno, lexpos, message
                )
            else:
                s = "%s: %d: Error: %s" % (
                    self.input_file, lineno, message
                )
        else:
            s = "%s: Error: %s" % (
                self.input_file, message
            )
        print(s, file=sys.stderr)

    def warning_out(self, message, lineno=None, lexpos=None):
        """Signal lexing warning."""
        if lineno is not None:
            if lexpos is not None:
                s = "%s: %d:%d Warning: %s" % (
                    self.input_file, lineno, lexpos, message
                )
            else:
                s = "%s: %d: Warning: %s" % (
                    self.input_file, lineno, message
                )
        else:
            s = "%s: Warning: %s" % (
                self.input_file, message
            )
        print(s, file=sys.stderr)

    # == REQUIRED LEXER INTERFACE ==

    def build(self):
        """
        Build a minimal lexer out of PLY and wrap it in a complete lexer
        for llama. By default, the lexer is optimized and accepts
        only ASCII input.
        """
        self.lexer = lex.lex(
            module=self,
            optimize=1,
            reflags=re.ASCII)

    # A wrapper around the function of the inner lexer
    def token(self):
        """
        Return a token to caller. Detect when <EOF> has been reached.
        Signal abnormal cases.
        """
        t = self.lexer.token()
        if not t:
            # Check for abnormal EOF
            st = self.lexer.current_state()
            if st == "comment":
                self.error_out(
                    "Unclosed comment reaching end of file.",
                    self.lexer.lineno
                )
            elif st == "string":
                self.error_out(
                    "Unclosed string reaching end of file.",
                    self.lexer.lineno
                )
            elif st == "char":
                self.error_out(
                    "Unclosed character literal at end of file.",
                    self.lexer.lineno
                )
            return None

        t.lexpos = self.lexer.lexpos - self.bol
        if self.debug:
            print((t.type, t.value, t.lineno, t.lexpos))
        return t

    def input(self, data):
        """Feed the lexer with input."""
        self.data = data
        self.lexer.input(self.data)

    def clone(self):
        newLexer = LlamaLexer(debug=self.debug)
        newLexer.build()
        newLexer.error = self.error
        newLexer.data = self.data
        newLexer.lexer = self.lexer.clone()
        newLexer.bol = self.bol
        newLexer.level = self.level
        return newLexer

    # == ITERATOR INTERFACE ==

    def __iter__(self):
        return self

    def __next__(self):
        t = self.token()
        if t is None:
            raise StopIteration
        return t

    # == LEXING OF NON-TOKENS ==

    # Ignored characters
    t_INITIAL_ignore = " \r\t"

    # Newlines
    def t_ANY_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        st = t.lexer.current_state()
        if st == "string":
            self.error_out(
                "String spanning multiple lines (unclosed string).",
                t.lineno
            )
            t.lexer.begin('INITIAL')
        elif st == "char":
            self.error_out(
                "Character spanning multiple lines (unclosed character).",
                t.lineno
            )
            t.lexer.begin('INITIAL')
        self.bol = t.lexer.lexpos

    # Single-line comments. Do not consume the newline.
    def t_SCOMMENT(self, t):
        r'--[^\n]*'
        pass

    t_comment_ignore = " \r\t"

    # Start of block comment
    def t_INITIAL_comment_LCOMMENT(self, t):
        r'\(\*'
        self.level += 1
        t.lexer.begin('comment')

    # End of block comment
    def t_comment_RCOMMENT(self, t):
        r'\*\)'
        if self.level > 1:
            self.level -= 1
        else:
            self.level = 0
            t.lexer.begin('INITIAL')

    # Ignore (almost) anything inside a block comment
    # but stop matching when '(', '*' or a newline appears.
    # Match each comment-initiating character seperately.
    def t_comment_SPECIAL(self, t):
        r'[(*]|[^\n(*]+'
        pass

    # == LEXING OF TOKENS CARRYING NO VALUE ==

    # Integer operators
    t_PLUS      = r'\+'
    t_MINUS     = r'-'
    t_TIMES     = r'\*'
    t_DIVIDE    = r'/'

    # Floating-point perators
    t_FPLUS     = r'\+\.'
    t_FMINUS    = r'-\.'
    t_FTIMES    = r'\*\.'
    t_FDIVIDE   = r'/\.'
    t_FPOW      = r'\*\*'

    # Boolean operators
    t_BAND      = r'&&'
    t_BOR       = r'\|\|'

    # Comparison operators
    t_LT        = r'<'
    t_GT        = r'>'
    t_LE        = r'<='
    t_GE        = r'>='
    t_EQ        = r'='
    t_NEQ       = r'<>'
    t_NATEQ     = r'=='
    t_NATNEQ    = r'!='

    # Pattern operators
    t_ARROW     = r'->'
    t_PIPE      = r'\|'

    # Assignment & dereference
    t_ASSIGN    = r':='
    t_BANG      = r'!'

    # Semicolon
    t_SEMICOLON = r';'

    # Delimeters
    t_LPAREN    = r'\('
    t_RPAREN    = r'\)'
    t_LBRACKET  = r'\['
    t_RBRACKET  = r'\]'
    t_COMMA     = r','
    t_COLON     = r':'

    # == LEXING OF VALUE-TOKENS ==

    # Constructor identifiers
    t_CONID     = r'[A-Z][A-Za-z0-9_]*'

    # Generic identifiers and reserved words
    def t_GENID(self, t):
        r'[a-z][A-Za-z0-9_]*'
        if t.value in _reserved_words:
            t.type = t.value.upper()
        return t

    # Floating-point constants
    def t_FCONST(self, t):
        r'\d+\.\d+([eE]([+\-]?)\d+)?'
        try:
            t.value = float(t.value)
        except OverflowError:
            self.error_out(
                "Floating-point constant is irrepresentable.",
                t.lineno,
                t.lexpos - self.bol + 1
            )
            t.value = 0.0
        return t

    # Integer constants
    def t_ICONST(self, t):
        r'\d+'
        t.value = int(t.value)
        if t.value > self.max_uint:
            self.error_out(
                "Integer constant is too big.",
                t.lineno,
                t.lexpos - self.bol + 1
            )
            t.value = 0
        return t

    # FIXME: Inappropriate (?)
    t_char_string_ignore = "\r\t"

    # Char constants
    def t_INITIAL_LCHAR(self, t):
        r'\''
        t.lexer.begin('char')

    def t_char_CCONST(self, t):
        r'(([^\\\'\"])|(\\[ntr0\'\"\\])|(\\x[a-fA-F0-9]{2}))(\'?)'
        # TODO: Unescape it
        if t.value[-1] != "'":
            self.error_out(
                "Unclosed character literal.",
                t.lineno,
                t.lexpos - self.bol + 1
            )
        t.value = t.value.rstrip("'")
        t.lexer.begin('INITIAL')
        return t

    def t_char_RCHAR(self, t):
        r'\''
        self.error_out(
            "Empty character literal not allowed.",
            t.lineno,
            t.lexpos - self.bol + 1
        )
        t.lexer.begin('INITIAL')

    # String constants
    # FIXME: Ask if empty string is valid
    def t_INITIAL_LSTRING(self, t):
        r'"'
        t.lexer.begin('string')

    def t_string_SCONST(self, t):
        r'(([^\\\'\"])|(\\[ntr0\'\"\\])|(\\x[a-fA-F0-9]{2}))+("?)'
        if t.value[-1] != '"':
            self.error_out(
                "Unclosed string literal.",
                t.lineno,
                t.lexpos - self.bol + 1
            )
        t.value = t.value.rstrip('"')
        t.lexer.begin('INITIAL')
        return t

    # Catch-all error reporting
    def t_ANY_error(self, t):
        self.error_out(
            "Illegal character '%s'" % t.value[0],
            t.lineno,
            t.lexpos - self.bol + 1
        )
        t.lexer.skip(1)
        t.lexer.begin('INITIAL')
