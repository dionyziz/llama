import unittest

import sure, mock

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

    def test_regression_attr_equality(self):
        raise unittest.SkipTest("re-enable me after #25 gets merged")

        tdef = TestAST._parse("type color = Red", "typedef")
        tdef2 = ast.TypeDefList(
            [ast.TDef(ast.User("color"), [ast.Constructor("Red")])]
        )

        try:
            tdef == tdef2
        except:
            self.assertTrue(False, "equality should not throw")


class TestASTMap(unittest.TestCase):
    def setUp(self):
        self._mockf = mock.Mock()
        self._mocko = mock.Mock()
        self._int = ast.Int()
        self._float = ast.Float()
        self._list = [self._int]
        self._one = ast.ConstExpression(ast.Int(), 1)
        self._two = ast.ConstExpression(ast.Int(), 2)
        self._three = ast.ConstExpression(ast.Int(), 3)
        self._foo = ast.GenidExpression("foo")

    def _assert_walk(self, root, f_calls, o_calls):
        ast.map(root, func=self._mockf)

        for args in f_calls:
            self._mockf.assert_any_call(args)

        ast.map(root, obj=self._mocko)
        for o_call in o_calls:
            if len(o_call) == 2:
                call, args = o_call
                once = True
            else:
                call, args, once = o_call
            func = getattr(self._mocko, 'map_' + call)
            if once:
                func.assert_called_once_with(args)
            else:
                func.assert_any_call(args)

    def test_node(self):
        self._assert_walk(self._int, [self._int], [('node', self._int)])

    def test_list(self):
        self._assert_walk(
            self._list,
            [self._list, self._int],
            [('list', self._list), ('builtin', self._int)]
        )

    def test_program(self):
        p = ast.Program(self._list)
        self._assert_walk(p, [p], [('program', p)])

    def test_letdef(self):
        l = ast.LetDef(self._list)
        self._assert_walk(l, [l], [('letdef', l)])

    def test_functiondef(self):
        f = ast.FunctionDef("foo", [], self._one)
        self._assert_walk(
            f,
            [f, [], self._one],
            [
                ('functiondef', f),
                ('def', f),
                ('list', []),
                ('expression', self._one)
            ]
        )

    def test_functiondef_with_type(self):
        f = ast.FunctionDef("foo", [], self._one, self._float)
        self._assert_walk(f, [self._float], [('float', self._float)])

    def test_param(self):
        p = ast.Param("bar", self._float)
        self._assert_walk(
            p, [p, self._float], [('param', p), ('float', self._float)]
        )

    def test_unaryexpression(self):
        e = ast.UnaryExpression("+", self._one)

        self._assert_walk(
            e,
            [e, self._one],
            [('unaryexpression', e),
             ('constexpression', self._one)]
        )

    def test_binaryexpression(self):
        e = ast.BinaryExpression(self._one, "+", self._two)

        self._assert_walk(
            e,
            [e, self._one, self._two],
            [('binaryexpression', e),
             ('constexpression', self._one, False)]
        )

    def test_constexpression(self):
        self._assert_walk(
            self._one,
            [self._one],
            [('constexpression', self._one),
             ('expression', self._one),
             ('builtin', self._int)]
        )

    def test_deleteexpression(self):
        d = ast.DeleteExpression(self._foo)
        self._assert_walk(
            d,
            [d, self._foo],
            [('deleteexpression', d),
             ('genidexpression', self._foo)]
        )

    def test_forexpression(self):
        f = ast.ForExpression(
            self._foo,
            self._one,
            self._two,
            self._three
        )
        
        self._assert_walk(
            f,
            [f, self._foo, self._one, self._two, self._three],
            [('forexpression', f),
             ('genidexpression', self._foo),
             ('constexpression', self._one, False),
             ('constexpression', self._two, False),
             ('constexpression', self._three, False)]
        )

    def test_letinexpression(self):
        l = ast.LetInExpression(
            ast.LetDef([
                ast.FunctionDef('x', [], self._one)
            ]),
            self._one
        )
