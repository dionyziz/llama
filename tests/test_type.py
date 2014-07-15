import itertools
import unittest

import sure

from compiler import ast, error, parse, type


class TestType(unittest.TestCase):

    parsers = {}

    @classmethod
    def setUpClass(cls):
        mock = error.LoggerMock()
        cls.parser = parse.Parser(
            logger=mock,
            optimize=False,
            debug=False
        )

    @classmethod
    def _parse(cls, data, start='program'):
        mock = error.LoggerMock()

        # memoization
        try:
            parser = TestType.parsers[start]
        except:
            parser = TestType.parsers[start] = parse.Parser(
                logger=mock,
                optimize=False,
                start=start,
                debug=False
            )

        tree = parser.parse(data=data)

        return tree

    @classmethod
    def _process_typedef(cls, typeDefListList):
        tree = cls.parser.parse(data=typeDefListList)
        mock = error.LoggerMock()
        typeTable = type.Table(logger=mock)
        for typeDef in tree:
            typeTable.process(typeDef)
        return typeTable.logger.success

    def tearDown(self):
        # FIXME: This shouldn't be useful anymore.
        TestType.parser.logger.clear()

    def test_smartdict(self):
        sd = type.Table.smartdict()
        t = ast.User("foo")
        t.lineno, t.lexpos = 1, 1
        sd[t] = "foo"
        sd[t].should.be.equal("foo")

        tt = ast.User("foo")
        tt.lineno, tt.lexpos = 0, 0
        ttt = sd.getKey(tt)
        ttt.lineno.should.be.equal(1)
        ttt.lexpos.should.be.equal(1)

        del sd[t]
        sd.get(t).should.be(None)
        sd.getKey(t).should.be(None)

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
            self.assertTrue(
                self._process_typedef(t),
                "'%s' type processing should be OK" % t
            )

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
            self.assertFalse(
                self._process_typedef(t),
                "'%s' type processing should not be OK" % t
            )

    def test_isarray(self):
        (type.Validator.is_array(ast.Array(ast.Int()))).should.be.true
        (type.Validator.is_array(ast.Array(ast.Int(), 2))).should.be.true
        (type.Validator.is_array(ast.Array(ast.User('foo')))).should.be.true

        (type.Validator.is_array(ast.User('foo'))).shouldnt.be.true
        for builtin_type in ast.builtin_types_map.values():
            (type.Validator.is_array(builtin_type)).shouldnt.be.true

    def _validate(self, t):
        mock = error.LoggerMock()
        validator = type.Validator(logger=mock)
        validator.validate(t)
        return mock.success

    def test_validate(self):
        for builtin_type in ast.builtin_types_map.values():
            self._validate(builtin_type()).should.be.ok

        t = ast.User('foo')
        self._validate(t).should.be.ok

        t = ast.Ref(ast.Int())
        self._validate(t).should.be.ok

        t = ast.Ref(ast.User('foo'))
        self._validate(t).should.be.ok

        # Can have a ref to a ref.
        t = ast.Ref(ast.Ref(ast.Int()))
        self._validate(t).should.be.ok

        t = ast.Array(ast.Int())
        self._validate(t).should.be.ok

        t = ast.Array(ast.Int(), 2)
        self._validate(t).should.be.ok

        t = ast.Array(ast.User('foo'))
        self._validate(t).should.be.ok

        # Can have an array of refs
        t = ast.Array(ast.Ref(ast.User('foo')))
        self._validate(t).should.be.ok

        t = ast.Function(ast.Int(), ast.Int())
        self._validate(t).should.be.ok

        t = ast.Function(ast.Ref(ast.Int()), ast.Int())
        self._validate(t).should.be.ok

        t = ast.Function(ast.Int(), ast.Ref(ast.Int()))
        self._validate(t).should.be.ok

        t = ast.Function(ast.Array(ast.Int()), ast.Int())
        self._validate(t).should.be.ok


        # Can't have a ref to an array.
        t = ast.Ref(ast.Array(ast.Int()))
        self._validate(t).shouldnt.be.ok

        # Can't have a ref to an array (nested).
        t = ast.Ref(ast.Ref(ast.Array(ast.Int())))
        self._validate(t).shouldnt.be.ok

        t = ast.Function(ast.Ref(ast.Array(ast.Int())), ast.Int())
        self._validate(t).shouldnt.be.ok

        # Can't have an array of array of ...
        t = ast.Array(ast.Array(ast.Int()))
        self._validate(t).shouldnt.be.ok

        t = ast.Function(ast.Array(ast.Array(ast.Int())), ast.Int())
        self._validate(t).shouldnt.be.ok

        # Can't have array as return type.
        t = ast.Function(ast.Int(), ast.Array(ast.Int()))
        self._validate(t).shouldnt.be.ok
