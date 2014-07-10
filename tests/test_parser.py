import unittest

import sure

from compiler import parse, lex, error, ast, type


class TestParser(unittest.TestCase):
    def setUp(self):
        self.parsers = {}

        self.one = self._parse("1", "expr")
        self.two = self._parse("2", "expr")
        self.true = self._parse("true", "expr")

    def _parse(self, data, start='program'):
        mock = error.LoggerMock()

        lexer = lex.Lexer(logger=mock, optimize=1)

        # memoization
        try:
            parser = self.parsers[start]
        except:
            parser = self.parsers[start] = parse.Parser(
                logger=mock,
                optimize=0,
                start=start,
                debug=0
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
        self._parse("(my_parameter: int)", "param").should.be.equal(ast.Param("my_parameter", ast.Int()))

    def test_builtin_type(self):
        self._parse("int", "builtin_type").should.be.equal(ast.Int())
        self._parse("int", "type").should.be.equal(ast.Int())

    def test_star_comma_seq(self):
        self._parse("*", "star_comma_seq").should.be.equal(1)
        self._parse("*, *, *", "star_comma_seq").should.be.equal(3)

    def test_array_type(self):
        self._parse("array of int", "array_type").should.be.equal(ast.Array(ast.Int()))
        self._parse("array [*, *] of int", "array_type").should.be.equal(ast.Array(ast.Int(), 2))

    def test_function_type(self):
        self._parse("int -> float", "function_type").should.be.equal(ast.Function(ast.Int(), ast.Float()))

    def test_ref_type(self):
        self._parse("int ref", "ref_type").should.be.equal(ast.Ref(ast.Int()))

    def test_user_type(self):
        self._parse("mytype", "user_type").should.be.equal(ast.User("mytype"))

    def test_type_paren(self):
        self._parse("(int)", "type").should.be.equal(ast.Int())

    def test_const(self):
        self._parse("5", "simple_expr").should.be.equal(ast.ConstExpression(ast.Int(), 5))
        self._parse("5.7", "simple_expr").should.be.equal(ast.ConstExpression(ast.Float(), 5.7))
        self._parse("'z'", "simple_expr").should.be.equal(ast.ConstExpression(ast.Char(), 'z'))
        self._parse('"z"', "simple_expr").should.be.equal(ast.ConstExpression(ast.String(), ['z', '\0']))
        self._parse("true", "simple_expr").should.be.equal(ast.ConstExpression(ast.Bool(), True))
        self._parse("()", "simple_expr").should.be.equal(ast.ConstExpression(ast.Unit(), None))

    def test_constr(self):
        self._parse("Node", "constr").should.be.equal(ast.Constructor("Node", []))
        self._parse("Node of int", "constr").should.be.equal(ast.Constructor("Node", [ast.Int()]))

    def test_simple_variable_def(self):
        self._parse("mutable foo", "simple_variable_def").should.be.equal(ast.VariableDef("foo"))
        self._parse("mutable foo : int", "simple_variable_def").should.be.equal(ast.VariableDef("foo", ast.Ref(ast.Int())))

    def test_array_variable_def(self):
        self._parse("mutable foo [2]", "array_variable_def").should.be.equal(ast.ArrayVariableDef("foo", [self.two]))
        self._parse("mutable foo [2] : int", "array_variable_def").should.be.equal(ast.ArrayVariableDef("foo", [self.two], ast.Array(ast.Int())))

    def test_while_expr(self):
        self._parse("while true do true done", "expr").should.be.equal(ast.WhileExpression(self.true, self.true))

    def _check_binary_operator(self, operator):
        expr = "1 %s 2" % operator
        parsed = self._parse(expr, "expr")
        self.assertTrue(isinstance(parsed, ast.BinaryExpression))
        self.assertEqual(parsed.operator, operator)
        self.assertEqual(parsed.leftOperand, self.one)
        self.assertEqual(parsed.rightOperand, self.two)

    def _check_unary_operator(self, operator):
        expr = "%s 1" % operator
        parsed = self._parse(expr, "expr")
        self.assertTrue(isinstance(parsed, ast.UnaryExpression), "Unary operator '%s' failed to parse as a unary expression" % operator)
        self.assertEqual(parsed.operator, operator, "Unary operator '%s' failed to parse; instead, it is parsing as '%s'" % (operator, parsed.operator))
        self.assertEqual(parsed.operand, self.one, "Unary operator '%s' did not correctly provide the value for its argument" % operator)

    def test_binary_expr(self):
        for operator in lex.binary_operators.keys():
            self._check_binary_operator(operator)

    def test_unary_expr(self):
        for operator in list(lex.unary_operators.keys()) + ["not"]:
            self._check_unary_operator(operator)

    def test_dim(self):
        dim = self._parse("dim name", "expr")

        self.assertTrue(isinstance(dim, ast.DimExpression))
        self.assertEqual(dim.name, "name")

        dim = self._parse("dim 2 name", "expr")

        self.assertTrue(isinstance(dim, ast.DimExpression))
        self.assertEqual(dim.name, "name")
        self.assertEqual(dim.dimension, 2)
