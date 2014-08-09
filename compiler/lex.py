"""
# ----------------------------------------------------------------------
# lexer.py
#
# Lexer for the Llama language
# http://courses.softlab.ntua.gr/compilers/2012a/llama2012.pdf
#
# Authors: Nick Korasidis <renelvon@gmail.com>
#          Dionysis Zindros <dionyziz@gmail.com>
#
# Lexer design is heavily inspired from the PHPLY lexer
# https://github.com/ramen/phply/blob/master/phply/phplex.py
# ----------------------------------------------------------------------
"""

import re

from ply import lex

from compiler import error

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
    type
    unit
    while
    with
    '''.split()
)

booleans = {
    'true': 'TRUE',
    'false': 'FALSE'
}

reserved_tokens = {s: s.upper() for s in reserved_words}
reserved_tokens.update(booleans)

escape_sequences = {
    r"\n": "\n",
    r"\t": "\t",
    r"\r": "\r",
    r"\0": "\0",
    r"\\": "\\",
    r"\'": "\'",
    r'\"': '\"'
}


def unescape(string):
    """Return unescaped string."""
    return bytes(string, 'ascii').decode('unicode_escape')


def explode(string):
    """Unescape, null-terminate and listify string."""
    string = list(unescape(string))
    string.append('\0')
    return string

binary_operators = {
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

    # Assignment
    ':=': 'ASSIGN',

    # Semicolon
    ';': 'SEMICOLON'
}

unary_operators = {
    # Assignment and dereference
    '!': 'BANG',

    # Sign operators
    '+': 'PLUS',
    '-': 'MINUS',
    '+.': 'FPLUS',
    '-.': 'FMINUS'
}

pattern_operators = {
    # Pattern operators
    '|': 'PIPE',
    '->': 'ARROW',
}

operators = dict(
    list(binary_operators.items()) +
    list(unary_operators.items()) +
    list(pattern_operators.items())
)

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


class _LexerFactory:
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

    def reset(self):
        """Reset the lexer's state."""
        self.bol = -1
        self.level = 0
        self.logger.clear()
        self.lexer.begin('INITIAL')
        self.lexer.lexpos = 0
        self.lexer.lineno = 1

    # == REQUIRED METHODS ==

    def build(self, **kwargs):
        """
        Build a lexer out of PLY and attach it to the wrapper object.

        NOTE: This function should be called once before ANY methods
        or attributes of the wrapper object are accessed.
        """
        self.lexer = lex.lex(module=self, **kwargs)

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
                self.logger.error(
                    "%d: error: Unclosed comment reaching end of file.",
                    self.lexer.lineno
                )
            elif state == "string":
                self.logger.error(
                    "%d: error: Unclosed string reaching end of file.",
                    self.lexer.lineno
                )
            elif state == "char":
                self.logger.error(
                    "%d: error: Unclosed character literal at end of file.",
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
        """Feed the lexer with input and reset the state."""
        self.lexer.input(lexdata)
        self.reset()

    def skip(self, value=1):
        """Skip 'value' characters in the input string."""
        self.lexer.skip(value)

    # == LEXING OF NON-TOKENS ==

    # Ignored characters
    t_INITIAL_comment_ignore = " \r\t"
    t_char_ignore = ""
    t_string_ignore = ""

    # Newlines
    def t_ANY_newline(self, tok):
        r'\n+'
        self.lexer.lineno += len(tok.value)
        self.bol = self.lexer.lexpos - 1

    # Single-line comments. Do not consume the newline.
    def t_SCOMMENT(self, _):
        r'--[^\n]*'
        pass

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

    # Generic identifiers, reserved words, boolean constants
    def t_GENID(self, tok):
        r'[a-z][A-Za-z0-9_]*'
        tok.type = reserved_tokens.get(tok.value, tok.type)

        booleans = {
            'TRUE': True,
            'FALSE': False
        }
        tok.value = booleans.get(tok.type, tok.value)

        return tok

    # Floating-point constants
    def t_FCONST(self, tok):
        r'\d+\.\d+([eE]([+\-]?)\d+)?'
        try:
            tok.value = float(tok.value)
        except OverflowError:
            self.logger.error(
                "%d:%d: error: Floating-point constant is irrepresentable.",
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

    # Regexes for well-formed char and string literals
    empty_char = r"''"
    escape_char_content = r'((\\[ntr0\'"\\])|(\\x[a-fA-F0-9]{2}))'

    # All printable ASCII except quotes and backslash.
    normal_char_content = r'((?!["\'\\])[\x20-\x7e])'

    char_content = r"(%s|%s)" % (normal_char_content, escape_char_content)
    proper_char = r"'%s'" % char_content
    proper_string = r'"%s*"' % char_content

    # Proper or empty char literal.
    @lex.TOKEN('(' + proper_char + ')|(' + empty_char + ')')
    def t_INITIAL_CCONST(self, tok):
        tok.value = tok.value[1:-1]
        if tok.value:
            tok.value = unescape(tok.value)[0]
        else:  # Illegal empty char
            self.logger.error(
                "%d:%d: error: Empty character literal not allowed.",
                tok.lineno,
                tok.lexpos - self.bol
            )
            tok.value = '\0'
        return tok

    # Malformed char literal ahead; enter 'char' state for recovery.
    def t_INITIAL_LCHAR(self, tok):
        r"'"
        self.logger.error(
            "%d:%d: error: Bad character literal.",
            tok.lineno,
            tok.lexpos - self.bol
        )
        self.lexer.begin('char')

    # Malformed char literal payload
    def t_char_CCONST(self, _):
        "[^'\n]+"
        pass

    # Exit recovery mode.
    def t_char_RCHAR(self, tok):
        r"'"
        tok.type = 'CCONST'
        tok.value = '\0'
        self.lexer.begin('INITIAL')
        return tok

    # Proper string literal
    @lex.TOKEN(proper_string)
    def t_INITIAL_SCONST(self, tok):
        tok.value = explode(tok.value[1:-1])
        # NOTE: Empty string is valid and is just the null byte.
        return tok

    # Malformed string literal ahead; enter 'string' state for recovery.
    def t_INITIAL_LSTRING(self, tok):
        r'"'
        self.logger.error(
            "%d:%d: error: Bad string literal.",
            tok.lineno,
            tok.lexpos - self.bol
        )
        self.lexer.begin('string')

    # Malformed string literal payload
    def t_string_SCONST(self, _):
        '[^\"\n]+'
        pass

    # Exit recovery mode
    def t_string_RSTRING(self, tok):
        r'"'
        tok.type = 'SCONST'
        tok.value = explode('')
        self.lexer.begin('INITIAL')
        return tok

    # Catch-all error reporting and panic recovery.
    def t_ANY_error(self, tok):
        state = self.lexer.current_state()
        state_msg = (" while inside %s" % state) if state != 'INITIAL' else ""
        self.logger.error(
            "%d:%d: error: Illegal character '%s'%s.",
            tok.lineno,
            tok.lexpos - self.bol,
            tok.value[0],
            state_msg
        )
        self.lexer.skip(1)
        self.lexer.begin('INITIAL')


class Lexer:
    """ A Llama lexer"""

    # The actual lexer as returned by _LexerFactory
    _lexer = None

    # Logger used for logging events. Possibly shared with other modules.
    logger = None

    def __init__(self, debug=False, optimize=True, logger=None, verbose=False):
        """
        Create a new lexer.

        By default, the lexer accepts only ASCII and is optimized (i.e
        caches the lexing tables across invocations).
        If a 'logger' is not provided, create one.
        For detailed reporting on regex construction, enable 'debug'.
        For echoing matched tokens to stdout, enable 'verbose'.
        """
        self.debug = debug
        self.optimize = optimize
        if logger is None:
            self.logger = error.Logger()
        else:
            self.logger = logger
        self.verbose = verbose

        self._lexer = _LexerFactory(logger=self.logger, verbose=verbose)
        self._lexer.build(debug=debug, optimize=optimize, reflags=re.ASCII)

    # == ITERATOR INTERFACE ==

    def __iter__(self):
        return self

    def __next__(self):
        tok = self.token()
        if tok is None:
            raise StopIteration
        return tok

    # == PUBLIC API ==

    def input(self, data):
        """Feed the lexer with input."""
        self._lexer.input(data)

    def skip(self, amount):
        """Skip the lexer 'amount' characters forward."""
        if self._lexer is None:
            raise Exception("Cannot skip over empty data.")
        self._lexer.skip(amount)

    def token(self):
        """Skip the lexer 'amount' characters forward."""
        if self._lexer is None:
            raise Exception("Cannot tokenize from empty data.")
        return self._lexer.token()

    def tokenize(self, data):
        """
        Lex the given string. Return an iterator over the string tokens.
        """
        self.input(data)
        return iter(self)

    # == EXPORT POSITION ATTRIBUTES ==

    @property
    def lexpos(self):
        """Return column following last token matched in current line."""
        return self._lexer.lexer.lexpos - self._lexer.bol

    @property
    def lineno(self):
        """Return current line of input"""
        return self._lexer.lexer.lineno


def tokenize(data, logger=None):
    """
    Lex the given string using the default Lexer.
    Return an iterator over the string tokens.
    """
    lexer = Lexer(logger=logger)
    return lexer.tokenize(data)


def quiet_tokenize(data):
    """
    Lex the given string using the default Lexer.
    Return an iterator over the string tokens.
    Explicitly silence errors/warnings.
    """
    return tokenize(data, logger=error.LoggerMock())
