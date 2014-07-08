import unittest

import sure

from compiler import parse, lex, error, ast, type


class TestParser(unittest.TestCase):
    def _parse(self, data, start='program'):
        mock = error.LoggerMock()

        lexer = lex.Lexer(logger=mock)
        parser = parse.Parser(
            logger=mock,
            optimize=0,
            start=start
        )

        tree = parser.parse(
            data=data,
            lexer=lexer
        )

        return tree

    def test_empty_program(self):
       self._parse("").should.be.equal(ast.Program([]))

    def test_empty_param_list(self):
        self._parse("", "param_list").should.be.equal([])

    def test_param_without_type(self):
        self._parse("my_parameter", "param").should.be.equal(ast.Param("my_parameter"))

    def test_param_with_type(self):
        self._parse("(my_parameter: int)", "param").should.be.equal(ast.Param("my_parameter", type.Int()))

    def test_builtin_type(self):
        self._parse("int", "builtin_type").should.be.equal(type.Int())
        self._parse("int", "type").should.be.equal(type.Int())

    def test_star_comma_seq(self):
        self._parse("*", "star_comma_seq").should.be.equal(1)
        self._parse("*, *, *", "star_comma_seq").should.be.equal(3)

    def test_array_type(self):
        self._parse("array of int", "array_type").should.be.equal(type.Array(type.Int()))
        self._parse("array [*, *] of int", "array_type").should.be.equal(type.Array(type.Int(), 2))

    def test_function_type(self):
        self._parse("int -> float", "function_type").should.be.equal(type.Function(type.Int(), type.Float()))

    def test_ref_type(self):
        self._parse("int ref", "ref_type").should.be.equal(type.Ref(type.Int()))

    def test_user_type(self):
        self._parse("mytype", "user_type").should.be.equal(type.User("mytype"))

    def test_type_paren(self):
        self._parse("(int)", "type").should.be.equal(type.Int())

    def test_const(self):
        self._parse("5", "simple_expr").should.be.equal(ast.ConstExpression(type.Int(), 5))
        self._parse("5.7", "simple_expr").should.be.equal(ast.ConstExpression(type.Float(), 5.7))
        self._parse("'z'", "simple_expr").should.be.equal(ast.ConstExpression(type.Char(), 'z'))
        self._parse('"z"', "simple_expr").should.be.equal(ast.ConstExpression(type.String(), ['z', '\0']))
        self._parse("true", "simple_expr").should.be.equal(ast.ConstExpression(type.Bool(), True))
        self._parse("()", "simple_expr").should.be.equal(ast.ConstExpression(type.Unit(), None))

    def test_constr(self):
        self._parse("Node", "constr").should.be.equal(ast.Constructor("Node", []))
        self._parse("Node of int", "constr").should.be.equal(ast.Constructor("Node", [type.Int()]))

    def test_simple_variable_def(self):
        self._parse("mutable foo", "simple_variable_def").should.be.equal(ast.VariableDef("foo"))
        self._parse("mutable foo : int", "simple_variable_def").should.be.equal(ast.VariableDef("foo", type.Int()))

    def test_array_variable_def(self):
        self._parse("mutable foo [2]", "array_variable_def").should.be.equal(ast.ArrayVariableDef("foo", [ast.ConstExpression(type.Int(), 2)]))
        self._parse("mutable foo [2] : int", "array_variable_def").should.be.equal(ast.ArrayVariableDef("foo", [ast.ConstExpression(type.Int(), 2)], type.Int()))

    def test_while_expr(self):
        self._parse("while true do true done", "expr").should.be.equal(ast.WhileExpression(ast.ConstExpression(type.Bool(), True), ast.ConstExpression(type.Bool(), True)))
