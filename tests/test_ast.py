import unittest

from compiler import ast, error, parse
from tests import parser_db

class TestAST(unittest.TestCase, parser_db.ParserDB):

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
