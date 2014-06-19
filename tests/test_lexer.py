import unittest
import sure
import lexer

class TestLexer(unittest.TestCase):
    def _lex_data(self, data):
        lex = lexer.Lexer() 
        lex.input(data)
        token_list = list(lex)
        return token_list

    def _assert_individual_token(self, input, expected_token_type, expected_token_value):
        l = self._lex_data(input)
        len(l).should.be.equal(1)
        tok = l[0]
        tok.type.should.be.equal(expected_token_type)
        tok.value.should.be.equal(expected_token_value)

    def test_empty(self):
        self._lex_data("").should.be.empty

    def test_keywords(self):
        for input_program, token in lexer.reserved_tokens.items():
            self._assert_individual_token(input_program, token, input_program)

    def test_genid(self):
        self._assert_individual_token("koko", "GENID", "koko")
        self._assert_individual_token("a", "GENID", "a")
        self._assert_individual_token(2048 * "koko", "GENID", 2048 * "koko")

    def test_conid(self):
        self._assert_individual_token("Koko", "CONID", "Koko")
        self._assert_individual_token("A", "CONID", "A")
        self._assert_individual_token(2048 * "Koko", "CONID", 2048 * "Koko")

    def test_iconst(self):
        self._assert_individual_token("42", "ICONST", 42)
        self._assert_individual_token("17", "ICONST", 17)
        self._assert_individual_token("0", "ICONST", 0)
        self._assert_individual_token("00042", "ICONST", 42)
