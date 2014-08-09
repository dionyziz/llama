import string
import unittest

from compiler import error, lex


class TestModuleAPI(unittest.TestCase):
    """Test the API of the lex module."""

    @staticmethod
    def test_tokenize():
        l1 = lex.Lexer()
        tokens1 = list(lex.tokenize(""))
        tokens2 = list(l1.tokenize(""))
        tokens1.should.equal(tokens2)

        mock = error.LoggerMock()
        l2 = lex.Lexer(logger=mock)
        tokens3 = list(lex.tokenize(""))
        tokens4 = list(l2.tokenize(""))
        tokens3.should.equal(tokens4)

    @staticmethod
    def test_quiet_tokenize():
        l1 = lex.Lexer(logger=error.LoggerMock())
        tokens1 = list(lex.quiet_tokenize(""))
        tokens2 = list(l1.tokenize(""))
        tokens1.should.equal(tokens2)


class TestLexerAPI(unittest.TestCase):
    """Test the API of the Lexer class."""

    @staticmethod
    def test_init():
        lexer1 = lex.Lexer()

        logger = error.LoggerMock()
        lexer2 = lex.Lexer(
            logger=logger,
            debug=False,
            optimize=True,
            verbose=False
        )
        lexer2.should.have.property("debug").being(False)
        lexer2.should.have.property("logger").being(logger)
        lexer2.should.have.property("optimize").being(True)
        lexer2.should.have.property("verbose").being(False)

    @staticmethod
    def test_input():
        lexer = lex.Lexer()
        lexer.input("foo")

    @staticmethod
    def test_skip():
        lexer = lex.Lexer()
        lexer.skip.when.called_with(1).should.throw(Exception)
        lexer.input("foo")
        lexer.skip(1)

    @staticmethod
    def test_token():
        lexer = lex.Lexer()
        lexer.token.when.called.should.throw(Exception)
        lexer.input("foo")
        t = lexer.token()

    @staticmethod
    def test_iterator():
        lexer = lex.Lexer()
        lexer.input("foo")
        i = iter(lexer)
        next(lexer)

    @staticmethod
    def test_tokenize():
        l1 = lex.Lexer()
        tokens1 = list(l1.tokenize(""))
        tokens1.should.equal([])
        l1.logger.success.should.be.true

        l2 = lex.Lexer(logger=error.LoggerMock())
        tokens2 = list(l2.tokenize("(*"))
        tokens2.should.equal([])
        l2.logger.success.should.be.false
        tokens3 = list(l2.tokenize(""))
        tokens3.should.equal([])
        l2.logger.success.should.be.true


class TestLexerRules(unittest.TestCase):
    """Test the Lexer's coverage of Llama vocabulary."""

    @staticmethod
    def _lex_data(input):
        lexer = lex.Lexer(logger=error.LoggerMock())
        tokens = list(lexer.tokenize(input))
        return tokens, lexer.logger

    def _assert_individual_token(self, input, expected_type, expected_value):
        tokens, logger = self._lex_data(input)
        tokens.should.have.length_of(1)
        tok = tokens[0]
        tok.type.shouldnt.be.different_of(expected_type)
        tok.value.should.equal(expected_value)
        logger.success.should.be.true

    def _assert_lex_success(self, input):
        _, logger = self._lex_data(input)
        logger.success.should.be.true

    def _assert_lex_failure(self, input):
        _, logger = self._lex_data(input)
        logger.success.should.be.false

    def test_empty(self):
        tokens, logger = self._lex_data("")
        tokens.should.be.empty
        logger.success.should.be.true

    def test_keywords(self):
        for input_program in lex.reserved_words:
            self._assert_individual_token(
                input_program,
                input_program.upper(),
                input_program
            )

    def test_genid(self):
        self._assert_individual_token("koko", "GENID", "koko")
        self._assert_individual_token("a", "GENID", "a")
        self._assert_individual_token(2048 * "koko", "GENID", 2048 * "koko")
        self._assert_individual_token("koko_lala", "GENID", "koko_lala")
        self._assert_individual_token("koko_42", "GENID", "koko_42")
        self._assert_individual_token("notakeyword", "GENID", "notakeyword")
        self._assert_individual_token("dimdim", "GENID", "dimdim")

        self._assert_lex_failure("_koko")
        self._assert_lex_failure("@koko")
        self._assert_lex_failure("\\koko")
        self._assert_lex_failure("\\x42")

        self._assert_individual_token("true", "TRUE", True)
        self._assert_individual_token("false", "FALSE", False)

    @unittest.skip("Enable me after bug #8 is fixed.")
    def test_nocolliding_ints_and_names(self):
        self._assert_lex_failure("42koko")
        self._assert_lex_failure("42Koko")

    def test_conid(self):
        self._assert_individual_token("Koko", "CONID", "Koko")
        self._assert_individual_token("A", "CONID", "A")
        self._assert_individual_token(2048 * "Koko", "CONID", 2048 * "Koko")

    def test_iconst(self):
        self._assert_individual_token("42", "ICONST", 42)
        self._assert_individual_token("17", "ICONST", 17)
        self._assert_individual_token("0", "ICONST", 0)
        self._assert_individual_token("00042", "ICONST", 42)
        self._assert_individual_token(
            "128374651837416253847123645812347",
            "ICONST",
            128374651837416253847123645812347
        )

    def test_fconst(self):
        self._assert_individual_token("42.5", "FCONST", 42.5)
        inputs = ["42.0", "4.2e1", "4.2E1", "0.420e+2", "420.0e-1", "420.0E-1"]
        for input in inputs:
            self._assert_individual_token(input, "FCONST", 42.0)

        self._assert_lex_success("5.41e-901721")

        self._assert_lex_failure("42.5.2")
        self._assert_lex_failure(".2")
        self._assert_lex_failure("4.2e1.0")

    def test_unescape(self):
        lex.unescape('\\n').should.equal('\n')

    def test_cconst(self):
        single_chars = set(string.printable) - set(string.whitespace) | {' '}
        for char in single_chars - {'"', "'", '\\'}:
            self._assert_individual_token(r"'%s'" % char, "CCONST", char)

        for escaped, literal in lex.escape_sequences.items():
            self._assert_individual_token(
                "'%s'" % (escaped),
                "CCONST",
                literal
            )

        self._assert_individual_token(r"'\x61'", "CCONST", "a")
        self._assert_individual_token(r"'\x1d'", "CCONST", "\x1d")

        self._assert_lex_failure(r"''")
        self._assert_lex_failure(r"'ab'")
        self._assert_lex_failure(r"'\xbad'")
        self._assert_lex_failure(r"'\xb'")
        self._assert_lex_failure(r"'\xg0'")
        self._assert_lex_failure("'\n'")
        self._assert_lex_failure(r"'a")
        self._assert_lex_failure(r"'")

    def test_sconst(self):
        for escaped, literal in lex.escape_sequences.items():
            self._assert_individual_token(
                '"%s"' % (escaped),
                "SCONST",
                [literal, '\0']
            )

        testcases = (
            r"",
            r"abc",
            r"Route66",
            r"Helloworld!\n",
            r"\"",
            r"Name:\t\"DouglasAdams\"\nValue\t42\n",
            r"play L\0L",
            r"an e\\xtra la\\zy string"
        )

        for input in testcases:
            self._assert_individual_token(
                '"%s"' % (input),
                "SCONST",
                lex.explode(input)
            )

        self._assert_lex_failure('"')
        self._assert_lex_failure('"\'"')
        self._assert_lex_failure('"\n"')
        self._assert_lex_failure('"\na')

    def test_operators(self):
        for input, token in lex.operators.items():
            self._assert_individual_token(input, token, input)

    def test_delimiters(self):
        for input, token in lex.delimiters.items():
            self._assert_individual_token(input, token, input)

    def test_comments(self):
        self._assert_lex_success('-- just a comment')
        self._assert_lex_success('-- comment (* let "" \'\'')
        self._assert_lex_success('--')
        self._assert_lex_success('---')

        self._assert_lex_success('(* comment *)')
        self._assert_lex_success('(**)')
        self._assert_lex_success('(***)')
        self._assert_lex_success('(*(**)*)')
        self._assert_lex_success('(*(*\n*)\n*)')

        self._assert_lex_failure('(*')
        self._assert_lex_failure('(*(**)')

    def test_misc(self):
        not_operators = r'\#$%&.?@^_`~'
        for symbol in not_operators:
            self._assert_lex_failure(symbol)
