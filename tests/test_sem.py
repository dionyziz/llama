import unittest

import sure, mock

from compiler import ast, sem


class TestSem(unittest.TestCase):
    def setUp(self):
        self.m = mock.Mock()
        self.t = ast.Int()
        self.l = [self.t]

    def test_node(self):
        sem.walk(self.t, self.m)
        self.m.assert_called_once_with(self.t)

    def test_list(self):
        sem.walk(self.l, self.m)
        self.m.assert_any_call(self.t)

    def test_program(self):
        sem.walk(ast.Program(self.l), self.m)
        self.m.assert_any_call(self.t)

    def test_letdef(self):
        sem.walk(ast.LetDef(self.l), self.m)
        self.m.assert_any_call(self.t)
