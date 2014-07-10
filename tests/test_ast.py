import unittest

import sure

from compiler import ast


class TestAST(unittest.TestCase):
    def test_eq(self):
        ast.Constructor("foo", []).should.be.equal(ast.Constructor("foo", []))
        ast.Constructor("foo", []).shouldnt.be.equal(ast.Constructor("bar", []))
