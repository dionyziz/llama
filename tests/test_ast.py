import itertools
import unittest

import sure, mock

from compiler import ast
from tests import parser_db


class TestAST(unittest.TestCase, parser_db.ParserDB):

    def test_eq(self):
        foocon = ast.Constructor("foo", [])
        ast.Constructor("foo", []).should.equal(foocon)
        ast.Constructor("bar", []).shouldnt.equal(foocon)

    def test_regression_constructor_attr_equality(self):
        tdef1 = self._parse("type color = Red", "typedef")
        tdef2 = [ast.TDef(ast.User("color"), [ast.Constructor("Red")])]

        node_eq = lambda a, b: a == b
        node_eq.when.called_with(tdef1, tdef2).shouldnt.throw(AttributeError)

    def test_builtin_type_equality(self):
        for typecon in ast.builtin_types_map.values():
            typecon().should.equal(typecon())

        for typecon1, typecon2 in itertools.combinations(
            ast.builtin_types_map.values(), 2
        ):
            typecon1().shouldnt.equal(typecon2())

    def test_builtin_type_set(self):
        typeset = {typecon() for typecon in ast.builtin_types_map.values()}
        typeset.add(ast.User("foo"))
        for typecon in ast.builtin_types_map.values():
            typeset.should.contain(typecon())
        typeset.should.contain(ast.User("foo"))
        typeset.shouldnt.contain(ast.User("bar"))

    def test_user_defined_types(self):
        ast.User("foo").should.equal(ast.User("foo"))

        ast.User("foo").shouldnt.equal(ast.User("bar"))
        ast.User("foo").shouldnt.equal(ast.Int())

    def test_ref_types(self):
        footype = ast.User("foo")
        bartype = ast.User("bar")
        reffootype = ast.Ref(footype)

        reffootype.should.equal(ast.Ref(footype))

        reffootype.shouldnt.equal(footype)
        reffootype.shouldnt.equal(ast.Ref(bartype))

    def test_array_types(self):
        inttype = ast.Int()
        ast.Array(inttype).should.equal(ast.Array(inttype))
        ast.Array(inttype, 2).should.equal(ast.Array(inttype, 2))

        ast.Array(ast.Int()).shouldnt.equal(ast.Array(ast.Float()))
        ast.Array(inttype, 1).shouldnt.equal(ast.Array(inttype, 2))

        arr_int_type = ast.Array(inttype)
        arr_int_type.shouldnt.equal(inttype)
        arr_int_type.shouldnt.equal(ast.User("foo"))
        arr_int_type.shouldnt.equal(ast.Ref(inttype))

    def test_function_types(self):
        intt = ast.Int()
        ast.Function(intt, intt).should.equal(ast.Function(intt, intt))

        i2float = ast.Function(ast.Int(), ast.Float())
        i2float.shouldnt.equal(ast.Function(ast.Float(), ast.Int()))

        i2float.shouldnt.equal(intt)
        i2float.shouldnt.equal(ast.User("foo"))
        i2float.shouldnt.equal(ast.Ref(ast.Int()))
        i2float.shouldnt.equal(ast.Array(ast.Int()))


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

    def _assert_walk(self, root, o_calls):
        ast.map(root, obj=self._mocko)
        ast.map(root, func=self._mockf)

        count_calls = {}
        for o_call in o_calls:
            if o_call[0] not in count_calls:
                count_calls[o_call[0]] = 0
            count_calls[o_call[0]] += 1

        for o_call in o_calls:
            if len(o_call) == 1:
                call, = o_call
                args = root
            if len(o_call) == 2:
                call, args = o_call
            if len(o_call) == 3:
                call, args, once = o_call
            else:
                if count_calls[call] > 1:
                    once = False
                else:
                    once = True
            self._mockf.assert_any_call(args)
            func = getattr(self._mocko, "map_" + call)
            if once:
                func.assert_called_once_with(args)
            else:
                func.assert_any_call(args)

    def test_node(self):
        self._assert_walk(self._int, [("node",)])

    def test_list(self):
        self._assert_walk(
            self._list,
            [("list",), ("builtin", self._int)]
        )

    def test_program(self):
        p = ast.Program(self._list)
        self._assert_walk(p, [("program",)])

    def test_letdef(self):
        l = ast.LetDef(self._list)
        self._assert_walk(l, [("letdef",)])

    def test_functiondef(self):
        f = ast.FunctionDef("foo", [], self._one)
        self._assert_walk(
            f,
            [
                ("functiondef",),
                ("def", f),
                ("list", []),
                ("expression", self._one)
            ]
        )

    def test_functiondef_with_type(self):
        f = ast.FunctionDef("foo", [], self._one, self._float)
        self._assert_walk(f, [("float", self._float)])

    def test_param(self):
        p = ast.Param("bar", self._float)
        self._assert_walk(
            p, [("param",), ("float", self._float)]
        )

    def test_unaryexpression(self):
        e = ast.UnaryExpression("+", self._one)

        self._assert_walk(
            e,
            [("unaryexpression",),
             ("constexpression", self._one)]
        )

    def test_binaryexpression(self):
        e = ast.BinaryExpression(self._one, "+", self._two)

        self._assert_walk(
            e,
            [("binaryexpression",),
             ("constexpression", self._one),
             ("constexpression", self._two)]
        )

    def test_constexpression(self):
        self._assert_walk(
            self._one,
            [("constexpression",),
             ("expression",),
             ("builtin", self._int)]
        )

    def test_deleteexpression(self):
        d = ast.DeleteExpression(self._foo)
        self._assert_walk(
            d,
            [("deleteexpression",),
             ("genidexpression", self._foo)]
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
            [("forexpression",),
             ("genidexpression", self._foo),
             ("constexpression", self._one),
             ("constexpression", self._two),
             ("constexpression", self._three)]
        )

    def test_letinexpression(self):
        letdef = ast.LetDef([ast.FunctionDef("x", [], self._one)])
        letin = ast.LetInExpression(letdef, self._two)

        self._assert_walk(
            letin,
            [("letinexpression",),
             ("letdef", letdef),
             ("constexpression", self._two, False)]
        )

    def test_ifexpression(self):
        ifexpr = ast.IfExpression(self._one, self._two, self._three)

        self._assert_walk(
            ifexpr,
            [("ifexpression",),
             ("constexpression", self._one),
             ("constexpression", self._two),
             ("constexpression", self._three)]
        )

    def test_matchexpression(self):
        m = ast.MatchExpression(self._one, [])

        self._assert_walk(
            m,
            [("matchexpression",),
             ("constexpression", self._one),
             ("list", [])]
        )

    def test_clause(self):
        p = ast.Pattern(self._foo, [])
        c = ast.Clause(p, self._one)

        self._assert_walk(
            c,
            [("clause",),
             ("pattern", p),
             ("expression", self._one, False)]
        )
    
    def test_newexpression(self):
        n = ast.NewExpression(self._foo)

        self._assert_walk(n, [("newexpression", n), ("genidexpression", self._foo)])

    def test_whileexpression(self):
        whileexpr = ast.WhileExpression(self._one, self._two)

        self._assert_walk(
            whileexpr,
            [("whileexpression",),
             ("expression", self._one),
             ("expression", self._two)]
        )

    def test_variabledef(self):
        d = ast.VariableDef(self._foo, self._float)

        self._assert_walk(
            d,
            [("variabledef",),
             ("float", self._float)]
        )

    def test_tdef(self):
        foo = ast.User("type")
        l = [ast.Constructor("constructor")]
        d = ast.TDef(foo, l)

        self._assert_walk(
            d,
            [("tdef",),
             ("list", l, False),
             ("user", foo)]
        )

    def test_regression_nomethod(self):
        class MapperMock:
            builtin_called = False

            def map_user(self, p):
                self.builtin_called = True

        m = MapperMock()
        ast.map(ast.TDef(ast.User('color'), [ast.Constructor('Red')]), obj=m)
        m.builtin_called.should.equal(True)
