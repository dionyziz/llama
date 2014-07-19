import unittest

import sure

from compiler import ast, error, parse


class TestAST(unittest.TestCase):

    parsers = {}

    @classmethod
    def _parse(cls, data, start='program'):
        mock = error.LoggerMock()

        # memoization
        try:
            parser = cls.parsers[start]
        except KeyError:
            parser = cls.parsers[start] = parse.Parser(
                logger=mock,
                optimize=False,
                start=start,
                debug=False
            )

        tree = parser.parse(data=data)

        return tree

    def test_eq(self):
        foocon = ast.Constructor("foo", [])
        ast.Constructor("foo", []).should.equal(foocon)
        ast.Constructor("bar", []).shouldnt.equal(foocon)

    @unittest.skip("Enable me after #25 is merged.")
    def test_regression_attr_equality(self):
        tdef1 = self._parse("type color = Red", "typedef")
        tdef2 = ast.TypeDefList(
            [ast.TDef(ast.User("color"), [ast.Constructor("Red")])]
        )

        node_eq = ast.Node.__eq__
        node_eq.when.called_with(tdef1, tdef2).shouldnt.throw(AttributeError)
