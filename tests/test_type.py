import itertools
import unittest

import sure
import ast
import type

class TestType(unittest.TestCase):
    
    type_builders = (type.Bool, type.Int, type.Float, type.Unit, type.Char)

    def test_builtin_type_equality(self):
        for t in self.type_builders:
            (t()).should.be.equal(t())

        for t1, t2 in itertools.combinations(self.type_builders, 2):
            (t1()).shouldnt.be.equal(t2())
        
    def test_builtin_type_set(self):
        typeset = {t() for t in self.type_builders}
        for t in self.type_builders:
            (typeset).should.contain(t())

    def test_user_defined_types(self):
        footype = type.User("foo")
        bartype = type.User("bar")
        for t in self.type_builders:
            (footype).shouldnt.be.equal(t())
        
        (footype).should.be.equal(type.User("foo"))
        (bartype).shouldnt.be.equal(type.User("foo"))

        reffootype = type.Ref(footype)
        refbartype = type.Ref(bartype)

        (reffootype).should.be.equal(type.Ref(footype))
        (refbartype).shouldnt.be.equal(type.Ref(footype))

    
    def test_array_types(self):
        myinttype = type.Int()

        for t in self.type_builders:
            (type.Array(t())).should.be.equal(type.Array(t()))

        
        for t1, t2 in itertools.combinations(self.type_builders, 2):
            (type.Array(t1())).shouldnt.be.equal(type.Array(t2()))
       
        (type.Array(myinttype, 1)).shouldnt.be.equal(type.Array(myinttype, 2))

    def test_function_types(self):
        
        for t in self.type_builders:
            (type.Function(t(),t())).should.be.equal(type.Function(t(),t()))


        for t1, t2 in itertools.combinations(self.type_builders, 2):
            (type.Function(t2(),t1())).shouldnt.be.equal(type.Function(t1(), t2()))
