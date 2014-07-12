import unittest

import sure

from compiler import parse, lex, error, ast, type


class TestParser(unittest.TestCase):
    parsers = {}

    @classmethod
    def setUpClass(cls):
        cls.one = cls._parse("1", "expr")
        cls.two = cls._parse("2", "expr")
        cls.true = cls._parse("true", "expr")

        cls.xfunc = cls._parse("let x = 1", "letdef")
        cls.yfunc = cls._parse("let y = 2", "letdef")

    @classmethod
    def _parse(self, data, start='program'):
        mock = error.LoggerMock()

        lexer = lex.Lexer(logger=mock, optimize=1)

        # memoization
        try:
            parser = TestParser.parsers[start]
        except:
            parser = TestParser.parsers[start] = parse.Parser(
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


    def test_def_list(self):
        self._parse("", "def_list").should.be.equal([])
        self._parse("let x = 1", "def_list").should.be.equal([TestParser.xfunc])
        self._parse("let x = 1 let y = 2", "def_list").should.be.equal([TestParser.xfunc, TestParser.yfunc])

    def test_letdef(self):
        letdef = ast.LetDef(
            [ast.FunctionDef("x", [], TestParser.one)]
        )
        letdefrec = ast.LetDef(
            [ast.FunctionDef("x", [], TestParser.one)], True
        )
        self._parse("let x = 1", "letdef").should.be.equal(letdef)
        self._parse("let rec x = 1", "letdef").should.be.equal(letdefrec)

    def test_function_def(self):
        xfunc = ast.FunctionDef("x", [], TestParser.one)
        self._parse("let x = 1", "def").should.be.equal(xfunc)
        self._parse("let x y (z:int) = 1", "def").should.be.equal(
            ast.FunctionDef("x", [ast.Param("y"), ast.Param("z", ast.Int())], TestParser.one)
        )
        self._parse("let x y z:int = 1", "def").should.be.equal(
            ast.FunctionDef("x", [ast.Param("y"), ast.Param("z")], TestParser.one, ast.Int())
        )

    def test_param_list(self):
        self._parse("", "param_list").should.be.equal([])
        self._parse("my_param", "param_list").should.be.equal([ast.Param("my_param")])
        self._parse("a b", "param_list").should.be.equal([ast.Param("a"), ast.Param("b")])

    def test_param(self):
        self._parse("my_parameter", "param").should.be.equal(ast.Param("my_parameter"))
        self._parse("(my_parameter: int)", "param").should.be.equal(ast.Param("my_parameter", ast.Int()))
        self._parse("my_parameter: int", "param").should.be.equal(None)

    def test_builtin_type(self):
        self._parse("int", "type").should.be.equal(ast.Int())

    def test_star_comma_seq(self):
        self._parse("*", "star_comma_seq").should.be.equal(1)
        self._parse("*, *, *", "star_comma_seq").should.be.equal(3)

    def test_array_type(self):
        self._parse("array of int", "type").should.be.equal(ast.Array(ast.Int()))
        self._parse("array [*, *] of int", "type").should.be.equal(ast.Array(ast.Int(), 2))

    def test_function_type(self):
        self._parse("int -> float", "type").should.be.equal(ast.Function(ast.Int(), ast.Float()))

    def test_ref_type(self):
        self._parse("int ref", "type").should.be.equal(ast.Ref(ast.Int()))

    def test_user_type(self):
        self._parse("mytype", "type").should.be.equal(ast.User("mytype"))

    def test_type_paren(self):
        self._parse("(int)", "type").should.be.equal(ast.Int())

    def test_const(self):
        self._parse("5", "expr").should.be.equal(ast.ConstExpression(ast.Int(), 5))
        self._parse("5.7", "expr").should.be.equal(ast.ConstExpression(ast.Float(), 5.7))
        self._parse("'z'", "expr").should.be.equal(ast.ConstExpression(ast.Char(), 'z'))
        self._parse('"z"', "expr").should.be.equal(ast.ConstExpression(ast.String(), ['z', '\0']))
        self._parse("true", "expr").should.be.equal(ast.ConstExpression(ast.Bool(), True))
        self._parse("()", "expr").should.be.equal(ast.ConstExpression(ast.Unit(), None))

    def test_constr(self):
        self._parse("Node", "constr").should.be.equal(ast.Constructor("Node", []))
        self._parse("Node of int", "constr").should.be.equal(ast.Constructor("Node", [ast.Int()]))

    def test_simple_variable_def(self):
        self._parse("mutable foo : int", "def").should.be.equal(
            ast.VariableDef("foo", ast.Ref(ast.Int()))
        )

        self._parse("mutable foo", "def").should.be.equal(ast.VariableDef("foo"))

    def test_array_variable_def(self):
        self._parse("mutable foo [2]", "def").should.be.equal(ast.ArrayVariableDef("foo", [TestParser.two]))
        self._parse("mutable foo [2] : int", "def").should.be.equal(ast.ArrayVariableDef("foo", [TestParser.two], ast.Array(ast.Int())))

    def test_while_expr(self):
        self._parse("while true do true done", "expr").should.be.equal(ast.WhileExpression(self.true, self.true))

    def test_if_expr(self):
        self._parse("if true then true else true", "expr").should.be.equal(ast.IfExpression(self.true, self.true, self.true))
        self._parse("if true then true", "expr").should.be.equal(ast.IfExpression(self.true, self.true))

    def test_for_expr(self):
        self._parse("for i = 1 to 1 do true done", "expr").should.be.equal(ast.ForExpression("i", TestParser.one, TestParser.one, self.true))
        self._parse("for i = 1 downto 1 do true done", "expr").should.be.equal(ast.ForExpression("i", TestParser.one, TestParser.one, self.true, True))

    def test_pattern(self):
        self._parse("true", "pattern").should.be.equal(self.true)
        self._parse("Red true", "pattern").should.be.equal(ast.Pattern("Red", [self.true]))

    def test_match_expr(self):
        self._parse("match true with true -> true end", "expr").should.be.equal(ast.MatchExpression(self.true, [ast.Clause(self.true, self.true)]))

    def test_delete(self):
        self._parse("delete true", "expr").should.be.equal(ast.DeleteExpression(self.true))

    def _check_binary_operator(self, operator):
        expr = "1 %s 2" % operator
        parsed = self._parse(expr, "expr")
        self.assertTrue(isinstance(parsed, ast.BinaryExpression))
        self.assertEqual(parsed.operator, operator)
        self.assertEqual(parsed.leftOperand, TestParser.one)
        self.assertEqual(parsed.rightOperand, TestParser.two)

    def _check_unary_operator(self, operator):
        expr = "%s 1" % operator
        parsed = self._parse(expr, "expr")
        self.assertTrue(isinstance(parsed, ast.UnaryExpression), "Unary operator '%s' failed to parse as a unary expression" % operator)
        self.assertEqual(parsed.operator, operator, "Unary operator '%s' failed to parse; instead, it is parsing as '%s'" % (operator, parsed.operator))
        self.assertEqual(parsed.operand, TestParser.one, "Unary operator '%s' did not correctly provide the value for its argument" % operator)

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
