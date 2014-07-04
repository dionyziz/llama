import re
import unittest

import sure

import error
import lexer


class TestLexer(unittest.TestCase):
    def _lex_data(self, input):
        mock = error.LoggerMock()
        lex = lexer.Lexer(logger=mock)
        lex.input(input)
        token_list = list(lex)

        return (token_list, mock)

    def _assert_individual_token(self, input, expected_type, expected_value):
        l, mock = self._lex_data(input)
        len(l).should.be.equal(1)
        tok = l[0]
        tok.type.should.be.equal(expected_type)
        tok.value.should.be.equal(expected_value)
        mock.success.should.be.ok

    def _assert_lex_success(self, input):
        mock = error.LoggerMock()
        lex = lexer.Lexer(logger=mock)
        lex.input(input)
        list(lex)  # Force lexing
        mock.success.should.be.ok

    def _assert_lex_failure(self, input):
        mock = error.LoggerMock()
        lex = lexer.Lexer(logger=mock)
        lex.input(input)
        list(lex)  # Force lexing
        mock.success.shouldnt.be.ok

    def test_empty(self):
        l, mock = self._lex_data("")
        l.should.be.empty
        mock.success.should.be.ok

    def test_keywords(self):
        for input_program, token in lexer.reserved_tokens.items():
            self._assert_individual_token(input_program, token, input_program)

    def test_genid(self):
        self._assert_individual_token("koko", "GENID", "koko")
        self._assert_individual_token("a", "GENID", "a")
        self._assert_individual_token(2048 * "koko", "GENID", 2048 * "koko")
        self._assert_individual_token("koko_lala", "GENID", "koko_lala")
        self._assert_individual_token("koko_42", "GENID", "koko_42")
        self._assert_individual_token("notakeyword", "GENID", "notakeyword")
        self._assert_individual_token("dimdim", "GENID", "dimdim")

        self._assert_lex_success("42koko")

        self._assert_lex_failure("_koko")
        self._assert_lex_failure("@koko")
        self._assert_lex_failure("\\koko")
        self._assert_lex_failure("\\x42")

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
        lexer.unescape('\\n').should.be.equal('\n')

    def test_cconst(self):
        printable_ascii = set(map(chr, range(ord(' '), ord('~') + 1)))
        for c in printable_ascii - {'"', "'", '\\'}:
            self._assert_individual_token(r"'%s'" % c, "CCONST", c)

        for escaped, literal in lexer.escape_sequences.items():
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
        for escaped, literal in lexer.escape_sequences.items():
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
                lexer.explode(input)
            )

        self._assert_lex_failure('"')
        self._assert_lex_failure('"\'"')
        self._assert_lex_failure('"\n"')
        self._assert_lex_failure('"\na')

    def test_operators(self):
        for input, token in lexer.operators.items():
            self._assert_individual_token(input, token, input)

    def test_delimiters(self):
        for input, token in lexer.delimiters.items():
            self._assert_individual_token(input, token, input)

    def test_comments(self):
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
