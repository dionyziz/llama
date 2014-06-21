import itertools
import unittest

import sure
import ast
import type
import error as lm

class TestType(unittest.TestCase):
    
    builtin_builders = (type.Bool, type.Int, type.Float, type.Unit, type.Char)

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
        (type.User("foo")).should.be.equal(type.User("foo"))

        (type.User("foo")).shouldnt.be.equal(type.User("bar"))
        (type.User("foo")).shouldnt.be.equal(type.Int())

    def test_ref_types(self):
        footype = type.User("foo")
        bartype = type.User("bar")
        reffootype = type.Ref(footype)

        (reffootype).should.be.equal(type.Ref(footype))

        (reffootype).shouldnt.be.equal(footype)
        (reffootype).shouldnt.be.equal(type.Ref(bartype))

    def test_array_types(self):
        inttype = type.Int()
        (type.Array(inttype)).should.be.equal(type.Array(inttype))
        (type.Array(inttype, 2)).should.be.equal(type.Array(inttype, 2))

        (type.Array(type.Int())).shouldnt.be.equal(type.Array(type.Float()))
        (type.Array(inttype, 1)).shouldnt.be.equal(type.Array(inttype, 2))

        arrintType = type.Array(inttype)
        (arrintType).shouldnt.be.equal(inttype)
        (arrintType).shouldnt.be.equal(type.User("foo"))
        (arrintType).shouldnt.be.equal(type.Ref(inttype))

    def test_function_types(self):
        intt = type.Int()
        (type.Function(intt, intt)).should.be.equal(type.Function(intt, intt))

        i2float = type.Function(type.Int(), type.Float())
        (i2float).shouldnt.be.equal(type.Function(type.Float(), type.Int()))

        (i2float).shouldnt.be.equal(int)
        (i2float).shouldnt.be.equal(type.User("foo"))
        (i2float).shouldnt.be.equal(type.Ref(type.Int()))
        (i2float).shouldnt.be.equal(type.Array(type.Int()))
