import itertools
import unittest

import sure
from compiler import ast, error


class TestAST(unittest.TestCase):

    builtin_builders = ast.builtin_types_map.values()

    def test_eq(self):
        ast.Constructor("foo", []).should.be.equal(ast.Constructor("foo", []))
        ast.Constructor("foo", []).shouldnt.be.equal(ast.Constructor("bar", []))

    def test_builtin_type_equality(self):
        for t in self.builtin_builders:
            (t()).should.be.equal(t())

        for t1, t2 in itertools.combinations(self.builtin_builders, 2):
            (t1()).shouldnt.be.equal(t2())

    def test_builtin_type_set(self):
        typeset = {t() for t in self.builtin_builders}
        for t in self.builtin_builders:
            (typeset).should.contain(t())

    def test_user_defined_types(self):
        (ast.User("foo")).should.be.equal(ast.User("foo"))

        (ast.User("foo")).shouldnt.be.equal(ast.User("bar"))
        (ast.User("foo")).shouldnt.be.equal(ast.Int())

    def test_ref_types(self):
        footype = ast.User("foo")
        bartype = ast.User("bar")
        reffootype = ast.Ref(footype)

        (reffootype).should.be.equal(ast.Ref(footype))

        (reffootype).shouldnt.be.equal(footype)
        (reffootype).shouldnt.be.equal(ast.Ref(bartype))

    def test_array_types(self):
        inttype = ast.Int()
        (ast.Array(inttype)).should.be.equal(ast.Array(inttype))
        (ast.Array(inttype, 2)).should.be.equal(ast.Array(inttype, 2))

        (ast.Array(ast.Int())).shouldnt.be.equal(ast.Array(ast.Float()))
        (ast.Array(inttype, 1)).shouldnt.be.equal(ast.Array(inttype, 2))

        arrintType = ast.Array(inttype)
        (arrintType).shouldnt.be.equal(inttype)
        (arrintType).shouldnt.be.equal(ast.User("foo"))
        (arrintType).shouldnt.be.equal(ast.Ref(inttype))

    def test_function_types(self):
        intt = ast.Int()
        (ast.Function(intt, intt)).should.be.equal(ast.Function(intt, intt))

        i2float = ast.Function(ast.Int(), ast.Float())
        (i2float).shouldnt.be.equal(ast.Function(ast.Float(), ast.Int()))

        (i2float).shouldnt.be.equal(intt)
        (i2float).shouldnt.be.equal(ast.User("foo"))
        (i2float).shouldnt.be.equal(ast.Ref(ast.Int()))
        (i2float).shouldnt.be.equal(ast.Array(ast.Int()))
