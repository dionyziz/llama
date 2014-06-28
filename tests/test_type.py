import itertools
import unittest

import sure
from compiler import ast, error, lex, parse, type


class TestType(unittest.TestCase):

    builtin_builders = ast.builtin_map.values()

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

    def _process_typedef(self, typeDefListList):
        mock = error.LoggerMock()
        lexer = lex.Lexer(logger=mock, optimize=1)
        parser = parse.Parser(logger=mock, optimize=1)
        parser.parse(data=typeDefListList, lexer=lexer)
        return parser.logger.success

    def test_type_process(self):
        right_testcases = (
            "type color = Red | Green | Blue",
            "type list = Nil | Cons of int list",
            """
            type number = Integer of int | Real of float
                        | Complex of float float
            """,
            """
            type tree = Leaf | Node of int forest
            and  forest = Empty | NonEmpty of tree forest
            """
        )

        for t in right_testcases:
            self._process_typedef(t).should.be.ok

        wrong_testcases = (
            """
            -- No constructor reuse
            type dup = ConDup | ConDup
            """,
            """
            -- No reference to undefined type
            type what = What of undeftype
            """,
            """
            -- No type redefinition
            type same = Foo1
            type same = Foo2
            """,
            """
            -- No constructor sharing
            type one = Con
            type two = Con
            """,
            """
            -- No redefinition of builtin types
            type bool = BoolCon
            type char = CharCon
            type float = FloatCon
            type int = IntCon
            type unit = UnitCon
            """
        )

        for t in wrong_testcases:
            self._process_typedef(t).shouldnt.be.ok

    def test_isarray(self):
        (type.Table.is_array(ast.Array(ast.Int()))).should.be.true
        (type.Table.is_array(ast.Array(ast.Int(), 2))).should.be.true
        (type.Table.is_array(ast.Array(ast.User('foo')))).should.be.true

        (type.Table.is_array(ast.User('foo'))).shouldnt.be.true
        for builtin_type in ast.builtin_map.values():
            (type.Table.is_array(builtin_type)).shouldnt.be.true

    def _assert_validate_success(self, t):
        mock = error.LoggerMock()
        typeTable = type.Table(logger=mock)
        typeTable.validate(t)
        mock.success.should.be.ok

    def _assert_validate_failure(self, t):
        mock = error.LoggerMock()
        typeTable = type.Table(logger=mock)
        typeTable.validate(t)
        mock.success.shouldnt.be.ok

    def test_validate(self):
        for builtin_type in ast.builtin_map.values():
            self._assert_validate_success(builtin_type)

        t = ast.User('foo')
        self._assert_validate_success(t)

        t = ast.Ref(ast.Int())
        self._assert_validate_success(t)

        t = ast.Ref(ast.User('foo'))
        self._assert_validate_success(t)

        t = ast.Array(ast.Int())
        self._assert_validate_success(t)

        t = ast.Array(ast.Int(), 2)
        self._assert_validate_success(t)

        t = ast.Array(ast.User('foo'))
        self._assert_validate_success(t)

        t = ast.Array(ast.Ref(ast.User('foo')))
        self._assert_validate_success(t)

        t = ast.Function(ast.Int(), ast.Int())
        self._assert_validate_success(t)

        t = ast.Function(ast.Ref(ast.Int()), ast.Int())
        self._assert_validate_success(t)

        t = ast.Function(ast.Int(), ast.Ref(ast.Int()))
        self._assert_validate_success(t)

        t = ast.Function(ast.Array(ast.Int()), ast.Int())
        self._assert_validate_success(t)


        t = ast.Ref(ast.Array(ast.Int()))
        self._assert_validate_failure(t)

        t = ast.Ref(ast.Ref(ast.Array(ast.Int())))
        self._assert_validate_failure(t)

        t = ast.Array(ast.Array(ast.Int()))
        self._assert_validate_failure(t)

        t = ast.Array(ast.Ref(ast.Array(ast.Array(ast.Int()))))
        self._assert_validate_failure(t)

        t = ast.Function(ast.Int(), ast.Array(ast.Int()))
        self._assert_validate_failure(t)

        t = ast.Function(ast.Array(ast.Array(ast.Int())), ast.Int())
        self._assert_validate_failure(t)

        t = ast.Function(ast.Int(), ast.Ref(ast.Array(ast.Int())))
        self._assert_validate_failure(t)
