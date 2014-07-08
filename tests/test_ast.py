import unittest

import sure

from compiler import parse, lex, error, ast, type


class TestAST(unittest.TestCase):
    def test_eq(self):
        ast.Constructor("foo", []).should.be.equal(ast.Constructor("foo", []))
        ast.Constructor("foo", []).shouldnt.be.equal(ast.Constructor("bar", []))
