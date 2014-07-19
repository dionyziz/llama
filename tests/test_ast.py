import unittest

import sure

from compiler import ast, error, parse


class TestAST(unittest.TestCase):
# TODO: remove boilerplate code after simple_api branch gets merged

    parsers = {}

    @classmethod
    def _parse(cls, data, start='program'):
        mock = error.LoggerMock()

        # memoization
        try:
            parser = TestAST.parsers[start]
        except:
            parser = TestAST.parsers[start] = parse.Parser(
                logger=mock,
                optimize=False,
                start=start,
                debug=False
            )

        tree = parser.parse(data=data)

        return tree

    def test_eq(self):
        ast.Constructor("foo", []).should.be.equal(
            ast.Constructor("foo", [])
        )
        ast.Constructor("foo", []).shouldnt.be.equal(
            ast.Constructor("bar", [])
        )

    @unittest.skip("Enable me after #25 is merged.")
    def test_regression_attr_equality(self):
        tdef = TestAST._parse("type color = Red", "typedef")
        tdef2 = ast.TypeDefList(
            [ast.TDef(ast.User("color"), [ast.Constructor("Red")])]
        )

        try:
            tdef == tdef2
        except:
            self.assertTrue(False, "equality should not throw")
