import itertools
import unittest

from compiler import ast, error, parse, type
from tests import parser_db


class TestType(unittest.TestCase, parser_db.ParserDB):

    @classmethod
    def _process_typedef(cls, typedefListList):
        mock = error.LoggerMock()
        typeTable = type.Table(logger=mock)
        for typedefList in typedefListList:
            typeTable.process(typedefList)
        return typeTable.logger.success

    def test_type_process(self):
        proc = self._process_typedef
        error = type.LlamaBadTypeError

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

        for typedef in right_testcases:
            tree = self._parse(typedef)
            proc.when.called_with(tree).shouldnt.throw(error)

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

        for typedef in wrong_testcases:
            tree = self._parse(typedef)
            proc.when.called_with(tree).should.throw(error)

    def _is_array(self, t):
        return type.Validator.is_array(t)

    def test_isarray(self):
        for typecon in ast.builtin_types_map.values():
            self._is_array(typecon()).should.be.false

        right_testcases = (
            "array of int",
            "array of foo",
            "array [*, *] of int"
        )

        for type in right_testcases:
            tree = self._parse(type, 'type')
            self._is_array(tree).should.be.true

        wrong_testcases = (
            "foo",
            "int ref",
            "int -> int",
        )

        for type in wrong_testcases:
            tree = self._parse(type, 'type')
            self._is_array(tree).should.be.false

    def _validate(self, t):
        mock = error.LoggerMock()
        validator = type.Validator(logger=mock)
        validator.validate(t)
        return validator.logger.success

    def test_validate(self):
        proc = self._validate
        error = type.LlamaInvalidTypeError

        for typecon in ast.builtin_types_map.values():
            proc.when.called_with(typecon()).shouldnt.throw(error)

        right_testcases = (
            "foo",

            "int ref",
            "foo ref",
            "(int -> int) ref",
            "(int ref) ref",

            "array of int",
            "array of foo",
            "array of (int ref)",
            "array of (foo ref)",
            "array [*, *] of int",

            "int -> int",
            "foo -> int",
            "int -> foo",
            "int ref -> int",
            "int -> (int ref)",
            "(array of int) -> int"
            "int -> (array of int -> int)"
        )

        for typedef in right_testcases:
            tree = self._parse(typedef, 'type')
            proc.when.called_with(tree).shouldnt.throw(error)

        wrong_testcases = (
            "(array of int) ref",
            "(int -> array of int) ref",

            "array of (array of int)",
            "array of ((array of int) ref)",

            "int -> array of int"
            "int -> (int -> array of int)"
        )

        for typedef in wrong_testcases:
            tree = self._parse(typedef, 'type')
            proc.when.called_with(tree).should.throw(error)
