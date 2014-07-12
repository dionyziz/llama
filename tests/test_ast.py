import unittest

import sure

from compiler import ast, error, lex, parse


class TestAST(unittest.TestCase):
# TODO: remove boilerplate code after simple_api branch gets merged
    def setUp(self):
        self.parsers = {}

    def _parse(self, data, start='program'):
        mock = error.LoggerMock()

        lexer = lex.Lexer(logger=mock, optimize=1)

        # memoization
        try:
            parser = self.parsers[start]
        except:
            parser = self.parsers[start] = parse.Parser(
                logger=mock,
                optimize=0,
                start=start,
                debug=0
            )

        tree = parser.parse(
            data=data,
            lexer=lexer
        )

        return tree

    def test_eq(self):
        ast.Constructor("foo", []).should.be.equal(ast.Constructor("foo", []))
        ast.Constructor("foo", []).shouldnt.be.equal(ast.Constructor("bar", []))

    def test_regression_attr_equality(self):
        raise unittest.SkipTest("re-enable me after #25 gets merged")

        tdef = self._parse("type color = Red", "typedef")
        tdef2 = ast.TypeDefList([ast.TDef(ast.User("color"), [ast.Constructor("Red")])])

        try:
            tdef == tdef2
        except:
            self.assertTrue(False, "equality should not throw")
