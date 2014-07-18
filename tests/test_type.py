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
        mock = error.LoggerMock()
        typeTable = type.Table(logger=mock)
        for typeDefList in typeDefListList:
            typeTable.process(typeDefList)
        return typeTable.logger.success

    def tearDown(self):
        # FIXME: This shouldn't be useful anymore.
        TestType.parser.logger.clear()

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
            tree = self._parse(t)
            self.assertTrue(
                self._process_typedef(tree),
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
            tree = self._parse(t)
            self.assertFalse(
                self._process_typedef(tree),
                "'%s' type processing should not be OK" % t
            )

    def _is_array(self, t):
        return type.Validator.is_array(t)

    def test_isarray(self):
        right_testcases = (
            "array of int",
            "array of foo",
            "array [*, *] of int"
        )

        for t in right_testcases:
            tree = self._parse(t, 'type')
            self._is_array(tree).should.be.ok

        for builtin_type in ast.builtin_types_map.values():
            self._is_array(builtin_type()).shouldnt.be.ok

        wrong_testcases = (
            "foo",
            "int ref",
            "int -> int",
        )

        for t in wrong_testcases:
            tree = self._parse(t, 'type')
            self._is_array(tree).shouldnt.be.ok

    def _validate(self, t):
        mock = error.LoggerMock()
        validator = type.Validator(logger=mock)
        validator.validate(t)
        return mock.success

    def test_validate(self):
        for builtin_type in ast.builtin_types_map.values():
            self._validate(builtin_type()).should.be.ok

        right_testcases = (
            "foo",

            "int ref",
            "foo ref",
            "(int -> int) ref",
            "int ref ref",

            "array of int",
            "array of foo",
            "array [*, *] of int",
            "array of (foo ref)",

            "int -> int",
            "int ref -> int",
            "int -> (int ref)",
            "(array of int) -> int"
        )

        for t in right_testcases:
            tree = self._parse(t, 'type')
            self._validate(tree).should.be.ok

        wrong_testcases = (
            "array of int ref",
            "array of int ref ref",
            "array of int ref -> int",
            "array of (array of int)",
            "array of (array of int) -> int",
            "int -> array of int"
        )

        for t in wrong_testcases:
            tree = self._parse(t, 'type')
            self._validate(tree).shouldnt.be.ok
