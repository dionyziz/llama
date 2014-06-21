import itertools
import unittest

import sure
import ast
import type
import error as lm


class TestType(unittest.TestCase):

    builtin_builders = type.builtin_map.values()

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

    def _assert_typesem_success(self, typeDefListList):
        mock = lm.LoggerMock()
        typeTable = type.Table(logger=mock)
        for typeDefList in typeDefListList:
            typeTable.process(typeDefList)
        mock.success.should.be.ok

    def _assert_typesem_failure(self, typeDefListList):
        mock = lm.LoggerMock()
        typeTable = type.Table(logger=mock)
        for typeDefList in typeDefListList:
            typeTable.process(typeDefList)
        mock.success.shouldnt.be.ok

    def test_type_process(self):
        t = ast.TypeDefList([
            ast.TDef("color", [
                ast.Constructor("Red", []),
                ast.Constructor("Green", []),
                ast.Constructor("Blue", [])
            ])
        ])
        self._assert_typesem_success([t])

        """type list = Nil | Cons of int list"""
        t = ast.TypeDefList([
            ast.TDef("list", [
                ast.Constructor("Nil", []),
                ast.Constructor("Cons", [
                    type.Int(),
                    type.User("list")
                ])
            ])
        ])
        self._assert_typesem_success([t])

        """
        type number = Integer of int | Real of float
                    | Complex of float float
        """
        t = ast.TypeDefList([
            ast.TDef("number", [
                ast.Constructor("Integer", [
                    type.Int(),
                ]),
                ast.Constructor("Real", [
                    type.Float()
                ]),
                ast.Constructor("Complex", [
                    type.Float()
                ])
            ])
        ])
        self._assert_typesem_success([t])

        """
        type tree = Leaf | Node of int forest
        and  forest = Empty | NonEmpty of tree forest
        """
        t = ast.TypeDefList([
            ast.TDef("tree", [
                ast.Constructor("Leaf", []),
                ast.Constructor("Node", [
                    type.Int(),
                    type.User("forest")
                ])
            ]),
            ast.TDef("forest", [
                ast.Constructor("Empty", []),
                ast.Constructor("NonEmpty", [
                    type.User("tree"),
                    type.User("forest")
                ])
            ])
        ])
        self._assert_typesem_success([t])

        """
        -- No constructor reuse
        type dup = ConDup | ConDup
        """
        t = ast.TypeDefList([
            ast.TDef("dup", [
                ast.Constructor("ConDup", []),
                ast.Constructor("ConDup", [])
            ]),
        ])
        self._assert_typesem_failure([t])

        """
        -- No reference to undefined type
        type what = What of undeftype
        """
        t = ast.TypeDefList([
            ast.TDef("what", [
                ast.Constructor("What", [
                    type.User("undeftype")
                ])
            ])
        ])
        self._assert_typesem_failure([t])

        """
        -- No type redefinition
        type same = Foo1
        type same = Foo2
        """
        t1 = ast.TypeDefList([
            ast.TDef("same", [
                ast.Constructor("Foo1", [])
            ])
        ])
        t2 = ast.TypeDefList([
            ast.TDef("same", [
                ast.Constructor("Foo2", [])
            ])
        ])
        self._assert_typesem_failure([t1, t2])

        """
        -- No constructor sharing
        type one = Con
        type two = Con
        """
        t1 = ast.TypeDefList([
            ast.TDef("one", [
                ast.Constructor("Con", [])
            ])
        ])
        t2 = ast.TypeDefList([
            ast.TDef("two", [
                ast.Constructor("Con", [])
            ])
        ])
        self._assert_typesem_failure([t1, t2])

        """
        -- No redefinition of builtin types
        type bool = BoolCon
        type char = CharCon
        type float = FloatCon
        type int = IntCon
        type unit = UnitCon
        """
        t = ast.TypeDefList([
            ast.TDef("bool", [
                ast.Constructor("BoolCon", [])
            ])
        ])
        self._assert_typesem_failure([t])

        t = ast.TypeDefList([
            ast.TDef("char", [
                ast.Constructor("CharCon", [])
            ])
        ])
        self._assert_typesem_failure([t])

        t = ast.TypeDefList([
            ast.TDef("float", [
                ast.Constructor("FloatCon", [])
            ])
        ])
        self._assert_typesem_failure([t])

        t = ast.TypeDefList([
            ast.TDef("int", [
                ast.Constructor("IntCon", [])
            ])
        ])
        self._assert_typesem_failure([t])

        t = ast.TypeDefList([
            ast.TDef("unit", [
                ast.Constructor("UnitCon", [])
            ])
        ])
        self._assert_typesem_failure([t])
