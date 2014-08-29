import itertools
import unittest

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
