"""
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
"""

from error import DummyLogger
import ply.lex as lex

# Represent reserved words as a frozenset for fast lookup
reserved_words = frozenset('''
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

reserved_tokens = {s: s.upper() for s in reserved_words}

escape_sequences = {
    r"\n": "\n",
    r"\t": "\t",
    r"\r": "\r",
    r"\0": "\0",
    r"\\": "\\",
    r"\'": "\'",
    r'\"': '\"'
}

operators = {
    # Integer operators
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'TIMES',
    '/': 'DIVIDE',

    # Floating-point operators
    '+.': 'FPLUS',
    '-.': 'FMINUS',
    '*.': 'FTIMES',
    '/.': 'FDIVIDE',
    '**': 'FPOW',

    # Comparison operators
    '<': 'LT',
    '>': 'GT',
    '=': 'EQ',
    '<=': 'LE',
    '>=': 'GE',
    '<>': 'NEQ',
    '==': 'NATEQ',
    '!=': 'NATNEQ',

    # Boolean operators
    '&&': 'BAND',
    '||': 'BOR',

    # Pattern operators
    '|': 'PIPE',
    '->': 'ARROW',

    # Assignment and dereference
    '!': 'BANG',
    ':=': 'ASSIGN',

    # Semicolon
    ';': 'SEMICOLON'
}

delimiters = {
    '(': 'LPAREN',
    ')': 'RPAREN',
    '[': 'LBRACKET',
    ']': 'RBRACKET',
    ',': 'COMMA',
    ':': 'COLON'
}

other_tokens = (
    # Identifiers (generic variable identifiers, constructor identifiers)
    'GENID', 'CONID',

    # Literals (int constant, float constant, char constant, string const)
    'ICONST', 'FCONST', 'CCONST', 'SCONST'
)

# All valid_tokens [exported]
tokens = sum(
    (
        tuple(reserved_tokens.values()),
        tuple(operators.values()),
        tuple(delimiters.values()),
        other_tokens
    ),
    tuple()
)


class _LexerBuilder:
    """
    Implementation of a Llama lexer

    Defines tokens and lexing rules, performs error reporting,
    interacts with PLY and tracks line and column numbers.
    """

    # Token list needed by PLY module
    tokens = tokens

    # Lexer states
    states = (
        ('char', 'exclusive'),
        ('string', 'exclusive'),
        ('comment', 'exclusive')
    )

    # The raw lexer derived from PLY.
    lexer = None

    # If 'verbose' is True, each token will be stored as a DEBUG event.
    verbose = False

    # File position of the most recent beginning of line
    bol = -1

    # Levels of nested comment blocks still open
    level = 0

    # Logger used for recording events. Possibly shared with other modules.
    logger = None

    def __init__(self, logger, verbose=False):
        """
        Initialize wrapper object of PLY lexer. To get a working lexer,
        invoke build() on the returned object.
        """
        self.logger = logger
        self.verbose = verbose
        if self.verbose:
            self.logger.info(__name__ + ': _LexerBuilder: wrapper initialized')

    # == REQUIRED METHODS ==

    def build(self, **kwargs):
        """
        Build a lexer out of PLY and attach it to the wrapper object.

        NOTE: This function should be called once before ANY methods
        or attributes of the wrapper object are accessed.
        """
        self.lexer = lex.lex(module=self, **kwargs)
        if self.verbose:
            self.logger.info(__name__ + ': _LexerBuilder: lexer ready ')

    # A wrapper around the function of the inner lexer
    def token(self):
        """
        Return a token to caller. Detect when <EOF> has been reached.
        Signal abnormal cases.
        """
        tok = self.lexer.token()
        if tok is None:
            # Check for abnormal EOF
            state = self.lexer.current_state()
            if state == "comment":
                self.error_out(
                    "Unclosed comment reaching end of file.",
                    self.lexer.lineno
                )
            elif state == "string":
                self.error_out(
                    "Unclosed string reaching end of file.",
                    self.lexer.lineno
                )
            elif state == "char":
                self.error_out(
                    "Unclosed character literal at end of file.",
                    self.lexer.lineno
                )
            return None

        # Track the token's column instead of lexing position.
        tok.lexpos -= self.bol
        if self.verbose:
            self.logger.debug(
                "%d:%d\t%s\t%s",
                tok.lineno,
                tok.lexpos,
                tok.type,
                tok.value
            )
        return tok

    def input(self, lexdata):
        """Feed the lexer with input."""
        self.lexer.input(lexdata)

    def skip(self, value=1):
        """Skip 'value' characters in the input string."""
        self.lexer.skip(value)

    # == ERROR REPORTING ==

    def error_out(self, message, lineno=None, lexpos=None):
        """Signal lexing error."""
        if lineno is not None:
            if lexpos is not None:
                self.logger.error("%d:%d: error: %s", lineno, lexpos, message)
            else:
                self.logger.error("%d: error: %s", lineno, message)
        else:
            self.logger.error("error: %s", message)

    # == LEXING OF NON-TOKENS ==

    # Ignored characters
    t_INITIAL_ignore = " \r\t"

    # Newlines
    def t_ANY_newline(self, tok):
        r'\n+'
        self.lexer.lineno += len(tok.value)
        state = self.lexer.current_state()
        if state == "string":
            self.error_out(
                "String spanning multiple lines (unclosed string).",
                tok.lineno
            )
            self.lexer.begin('INITIAL')
        elif state == "char":
            self.error_out(
                "Character spanning multiple lines (unclosed character).",
                tok.lineno
            )
            self.lexer.begin('INITIAL')
        self.bol = self.lexer.lexpos - 1

    # Single-line comments. Do not consume the newline.
    def t_SCOMMENT(self, _):
        r'--[^\n]*'
        pass

    t_comment_ignore = " \r\t"

    # Start of block comment
    def t_INITIAL_comment_LCOMMENT(self, _):
        r'\(\*'
        self.level += 1
        self.lexer.begin('comment')

    # End of block comment
    def t_comment_RCOMMENT(self, _):
        r'\*\)'
        if self.level > 1:
            self.level -= 1
        else:
            self.level = 0
            self.lexer.begin('INITIAL')

    # Ignore (almost) anything inside a block comment
    # but stop matching when '(', '*' or a newline appears.
    # Match each comment-initiating character seperately.
    def t_comment_SPECIAL(self, _):
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
    def t_GENID(self, tok):
        r'[a-z][A-Za-z0-9_]*'
        try:
            tok.type = reserved_tokens[tok.value]
        except KeyError:
            pass
        return tok

    # Floating-point constants
    def t_FCONST(self, tok):
        r'\d+\.\d+([eE]([+\-]?)\d+)?'
        try:
            tok.value = float(tok.value)
        except OverflowError:
            self.error_out(
                "Floating-point constant is irrepresentable.",
                tok.lineno,
                tok.lexpos - self.bol
            )
            tok.value = 0.0
        return tok

    # Integer constants
    def t_ICONST(self, tok):
        r'\d+'
        tok.value = int(tok.value)
        # TODO Check if constant is too big in another module.
        return tok

    # FIXME: Inappropriate (?)
    t_char_string_ignore = "\r\t"

    # Char constants
    def t_INITIAL_LCHAR(self, _):
        r'\''
        self.lexer.begin('char')

    hex_char = r'\\x[a-fA-F0-9]{2}'
    escape_char = r'\\[ntr0"\'\\]'
    normal_char = r'[^\"\'\\]'
    char = r'((' + normal_char + r')|(' + escape_char + r')|(' + hex_char + r'))'
    rquoted_char = char + r'(\'?)'

    @lex.TOKEN(rquoted_char)
    def t_char_CCONST(self, tok):
        if tok.value[-1] != "'":
            self.error_out(
                "Unclosed character literal.",
                tok.lineno,
                tok.lexpos - self.bol
            )
        if tok.value[-1] == "'":
            tok.value = tok.value[:-1]
        if tok.value[0] == '\\':
            tok.value = _translate_escaped_character(tok.value)
        self.lexer.begin('INITIAL')
        return tok

    def t_char_RCHAR(self, tok):
        r'\''
        self.error_out(
            "Empty character literal not allowed.",
            tok.lineno,
            tok.lexpos - self.bol
        )
        self.lexer.begin('INITIAL')

    # String constants
    # FIXME: Ask if empty string is valid
    def t_INITIAL_LSTRING(self, _):
        r'"'
        self.lexer.begin('string')

    def t_string_SCONST(self, tok):
        r'(([^\\\'\"])|(\\[ntr0\'\"\\])|(\\x[a-fA-F0-9]{2}))+("?)'
        if tok.value[-1] != '"':
            self.error_out(
                "Unclosed string literal.",
                tok.lineno,
                tok.lexpos - self.bol
            )
        tok.value = tok.value.rstrip('"')
        self.lexer.begin('INITIAL')
        return tok

    # Catch-all error reporting
    def t_ANY_error(self, tok):
        self.error_out(
            "Illegal character '%s'" % tok.value[0],
            tok.lineno,
            tok.lexpos - self.bol
        )
        self.lexer.skip(1)
        self.lexer.begin('INITIAL')


class Lexer:
    """ A Llama lexer"""

    # The actual lexer as returned by _LexerBuilder
    _lexer = None

    # Logger used for logging events. Possibly shared with other modules.
    _logger = None

    # == REQUIRED METHODS (see _LexerBuilder for details) ==

    token = None
    input = None
    skip = None

    def __init__(self, logger=None, verbose=False, **kwargs):
        """Create a new lexer."""

        if logger is None:
            self._logger = DummyLogger()
        else:
            self._logger = logger

        self._lexer = _LexerBuilder(logger=logger, verbose=verbose)
        self._lexer.build(**kwargs)

        # Bind methods of interface to _LexerBuilder object methods.
        self.token = self._lexer.token
        self.input = self._lexer.input
        self.skip  = self._lexer.skip
        if verbose:
            self._logger.info(__name__ + ': Lexer: lexer ready')

    # == EXPORT POSITION ATTRIBUTES ==

    @property
    def lexpos(self):
        """Return column following last token matched in current line."""
        return self._lexer.lexer.lexpos - self._lexer.bol

    @property
    def lineno(self):
        """Return current line of input"""
        return self._lexer.lexer.lineno

    # == ITERATOR INTERFACE ==

    def __iter__(self):
        return self

    def __next__(self):
        tok = self.token()
        if tok is None:
            raise StopIteration
        return tok
