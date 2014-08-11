import unittest

from compiler import ast, type
from tests import parser_db


class TestTypeAPI(unittest.TestCase, parser_db.ParserDB):
    """Test the API of the type module."""

    @staticmethod
    def test_is_array():
        type.is_array(ast.Array(ast.Int())).should.be.true

    @staticmethod
    def test_array_of_array_error():
        exc = type.ArrayOfArrayError
        issubclass(exc, type.InvalidTypeError).should.be.true

    @staticmethod
    def test_array_return_error():
        exc = type.ArrayReturnError
        issubclass(exc, type.InvalidTypeError).should.be.true

    @staticmethod
    def test_ref_of_array_error():
        exc = type.RefOfArrayError
        issubclass(exc, type.InvalidTypeError).should.be.true

    @staticmethod
    def test_validate():
        type.validate(ast.Int())

    @staticmethod
    def test_redef_builtin_type_error():
        exc = type.RedefBuiltinTypeError
        issubclass(exc, type.BadTypeDefError).should.be.true

    @staticmethod
    def test_redef_constructor_error():
        exc = type.RedefConstructorError
        issubclass(exc, type.BadTypeDefError).should.be.true

    @staticmethod
    def test_redef_user_type_error():
        exc = type.RedefUserTypeError
        issubclass(exc, type.BadTypeDefError).should.be.true

    @staticmethod
    def test_undef_type_error():
        exc = type.UndefTypeError
        issubclass(exc, type.BadTypeDefError).should.be.true

    @staticmethod
    def test_table_init():
        type.Table()


class TestBase(unittest.TestCase, parser_db.ParserDB):
    def _assert_node_lineinfo(self, node):
        node.should.have.property("lineno")
        node.lineno.shouldnt.be(None)
        node.should.have.property("lexpos")
        node.lexpos.shouldnt.be(None)

class TestTable(TestBase):
    """Test the Table's processing of type definitions."""

    def test_type_process_correct(self):
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

        table = type.Table()
        proc = table.process
        for case in right_testcases:
            tree = self._parse(case, "typedef")
            proc.when.called_with(tree).shouldnt.throw(type.BadTypeDefError)


    def test_type_process_wrong(self):
        wrong_testcases = (
            (
                (
                    "type bool = BoolCon",
                    "type char = CharCon",
                    "type float = FloatCon",
                    "type int = IntCon",
                    "type unit = UnitCon",
                ),
                type.RedefBuiltinTypeError,
                1
            ),
            (
                (
                    "type dup = ConDup | ConDup",
                    """
                    type one = Con
                    type two = Con
                    """,
                ),
                type.RedefConstructorError,
                2
            ),
            (
                (
                    """
                    type same = Foo1
                    type same = Foo2
                    """,
                ),
                type.RedefUserTypeError,
                2
            ),
            (
                (
                    "type what = What of undeftype",
                ),
                type.UndefTypeError,
                1
            )
        )

        for cases, error, exc_node_count in wrong_testcases:
            for case in cases:
                table = type.Table()
                tree = self._parse(case)
                with self.assertRaises(error) as context:
                    for typeDefList in tree:
                        table.process(typeDefList)

                exc = context.exception
                exc.should.have.property("node")
                self._assert_node_lineinfo(exc.node)
                if exc_node_count == 2:
                    exc.should.have.property("prev")
                    exc.prev.shouldnt.be(exc.node)
                    self._assert_node_lineinfo(exc.prev)


class TestValidating(TestBase):
    """Test the validating of types."""

    def test_is_array(self):
        for typecon in ast.builtin_types_map.values():
            type.is_array(typecon()).should.be.false

        right_testcases = (
            "array of int",
            "array of foo",
            "array [*, *] of int"
        )

        for case in right_testcases:
            tree = self._parse(case, 'type')
            type.is_array(tree).should.be.true

        wrong_testcases = (
            "foo",
            "int ref",
            "int -> int",
        )

        for case in wrong_testcases:
            tree = self._parse(case, 'type')
            type.is_array(tree).should.be.false

    def test_validate(self):
        proc = type.validate
        error = type.InvalidTypeError

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
            "(array of int) -> int",
            "int -> (array of int -> int)",
            "(int -> int) -> int"
        )

        for case in right_testcases:
            tree = self._parse(case, 'type')
            proc.when.called_with(tree).shouldnt.throw(error)

        wrong_testcases = (
            (
                (
                    "array of (array of int)",
                    "(array of (array of int)) -> int",
                    "((array of (array of int)) -> int) ref",
                ),
                type.ArrayOfArrayError
            ),
            (
                (
                    "(array of int) ref",
                    "((array of int) ref) -> int",
                    "array of ((array of int) ref)",
                ),
                type.RefOfArrayError
            ),
            (
                (
                    "int -> array of int",
                    "int -> (int -> array of int)",
                    "(int -> array of int) ref",
                ),
                type.ArrayReturnError
            ),
        )

        for cases, error in wrong_testcases:
            for case in cases:
                tree = self._parse(case, "type")
                with self.assertRaises(error) as context:
                    proc(tree)
                exc = context.exception
                exc.should.have.property("node")

                self._assert_node_lineinfo(exc.node)
