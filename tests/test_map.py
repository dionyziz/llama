import unittest

import sure, mock

from compiler import ast


class TestASTMap(unittest.TestCase):
    def setUp(self):
        self.m = mock.Mock()
        self.t = ast.Int()
        self.l = [self.t]

    def test_node(self):
        ast.map(self.t, self.m)
        self.m.assert_called_once_with(self.t)

    def test_list(self):
        ast.map(self.l, self.m)
        self.m.assert_any_call(self.t)

    def test_program(self):
        ast.map(ast.Program(self.l), self.m)
        self.m.assert_any_call(self.t)

    def test_letdef(self):
        ast.map(ast.LetDef(self.l), self.m)
        self.m.assert_any_call(self.t)
