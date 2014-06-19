import unittest
import sure
import lexer


class LoggerMock():
    lexing_success = True

    def error(self, *args):
        self.lexing_success = False
    def warning(self, *args):
        pass
    def debug(self, *args):
        pass
    def info(self, *args):
        pass

class TestLexer(unittest.TestCase):
    def _lex_data(self, input):
        mock = LoggerMock()
        lex = lexer.Lexer(logger=mock)
        lex.input(input)
        token_list = list(lex)

        return (token_list, mock)

    def _assert_individual_token(self, input, expected_token_type, expected_token_value):
        l, mock = self._lex_data(input)
        len(l).should.be.equal(1)
        tok = l[0]
        tok.type.should.be.equal(expected_token_type)
        tok.value.should.be.equal(expected_token_value)
        mock.lexing_success.should.be.ok

    def _assert_lex_failed(self, input):
        mock = LoggerMock()
        lex = lexer.Lexer(logger=mock)
        lex.input(input)
        # force evaluation
        list(lex)
        mock.lexing_success.shouldnt.be.ok

    def test_empty(self):
        l, mock = self._lex_data("")
        l.should.be.empty
        mock.lexing_success.should.be.ok

    def test_keywords(self):
        for input_program, token in lexer.reserved_tokens.items():
            self._assert_individual_token(input_program, token, input_program)

    def test_genid(self):
        self._assert_individual_token("koko", "GENID", "koko")
        self._assert_individual_token("a", "GENID", "a")
        self._assert_individual_token(2048 * "koko", "GENID", 2048 * "koko")
        self._assert_individual_token("koko_lala", "GENID", "koko_lala")
        self._assert_individual_token("koko_42", "GENID", "koko_42")

    def test_conid(self):
        self._assert_individual_token("Koko", "CONID", "Koko")
        self._assert_individual_token("A", "CONID", "A")
        self._assert_individual_token(2048 * "Koko", "CONID", 2048 * "Koko")

    def test_iconst(self):
        self._assert_individual_token("42", "ICONST", 42)
        self._assert_individual_token("17", "ICONST", 17)
        self._assert_individual_token("0", "ICONST", 0)
        self._assert_individual_token("00042", "ICONST", 42)
