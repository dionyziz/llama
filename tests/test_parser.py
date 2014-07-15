import unittest

import sure

from compiler import ast, error, lex, parse, type


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

        # memoization
        try:
            parser = TestParser.parsers[start]
        except:
            parser = TestParser.parsers[start] = parse.Parser(
                logger=mock,
                optimize=False,
                start=start,
                debug=False
            )

        tree = parser.parse(data=data)

        return tree

    def test_parse(self):
        parse.parse("").should.be.equal(ast.Program([]))
        mock = error.LoggerMock()
        parse.parse("", logger=mock).should.be.equal(ast.Program([]))

    def test_empty_program(self):
        self._parse("").should.be.equal(ast.Program([]))

    def test_def_list(self):
        self._parse("", "def_list").should.be.equal([])

        self._parse("let x = 1", "def_list").should.be.equal(
            [TestParser.xfunc]
        )

        self._parse("let x = 1 let y = 2", "def_list").should.be.equal(
            [TestParser.xfunc, TestParser.yfunc]
        )

    def test_letdef(self):
        self._parse("let x = 1", "letdef").should.be.equal(
            ast.LetDef(
                [ast.FunctionDef("x", [], TestParser.one)]
            )
        )
        self._parse("let rec x = 1", "letdef").should.be.equal(
            ast.LetDef(
                [ast.FunctionDef("x", [], TestParser.one)], True
            )
        )

    def test_function_def(self):
        self._parse("let x = 1", "def").should.be.equal(
            ast.FunctionDef("x", [], TestParser.one)
        )

        self._parse("let x y (z:int) = 1", "def").should.be.equal(
            ast.FunctionDef(
                "x",
                [ast.Param("y"), ast.Param("z", ast.Int())],
                TestParser.one
            )
        )

        self._parse("let x y z:int = 1", "def").should.be.equal(
            ast.FunctionDef(
                "x",
                [ast.Param("y"), ast.Param("z")], TestParser.one, ast.Int()
            )
        )

    def test_param_list(self):
        self._parse("", "param_list").should.be.equal([])

        self._parse("my_param", "param_list").should.be.equal(
            [ast.Param("my_param")]
        )

        self._parse("a b", "param_list").should.be.equal(
            [ast.Param("a"), ast.Param("b")]
        )

    def test_param(self):
        self._parse("my_parameter", "param").should.be.equal(
            ast.Param("my_parameter")
        )
        self._parse("(my_parameter: int)", "param").should.be.equal(
            ast.Param("my_parameter", ast.Int())
        )
        self._parse("my_parameter: int", "param").should.be.equal(None)

    def test_builtin_type(self):
        for type_name, type_node in ast.builtin_types_map.items():
            self._parse(type_name, "type").should.be.equal(type_node())

    def test_star_comma_seq(self):
        self._parse("*", "star_comma_seq").should.be.equal(1)
        self._parse("*, *, *", "star_comma_seq").should.be.equal(3)

    def test_array_type(self):
        array_node = ast.Array(ast.Int())
        self._parse("array of int", "type").should.be.equal(array_node)
        self._parse("array [*, *] of int", "type").should.be.equal(
            ast.Array(ast.Int(), 2)
        )

    def test_function_type(self):
        func_node = ast.Function(ast.Int(), ast.Float())
        self._parse("int -> float", "type").should.be.equal(func_node)

    def test_ref_type(self):
        ref_node = ast.Ref(ast.Int())
        self._parse("int ref", "type").should.be.equal(ref_node)

    def test_user_type(self):
        user_node = ast.User("mytype")
        self._parse("mytype", "type").should.be.equal(user_node)

    def test_type_paren(self):
        self._parse("(int)", "type").should.be.equal(ast.Int())

    def test_const(self):
        self._parse("5", "expr").should.be.equal(
            ast.ConstExpression(ast.Int(), 5)
        )
        self._parse("5.7", "expr").should.be.equal(
            ast.ConstExpression(ast.Float(), 5.7)
        )
        self._parse("'z'", "expr").should.be.equal(
            ast.ConstExpression(ast.Char(), 'z')
        )
        self._parse('"z"', "expr").should.be.equal(
            ast.ConstExpression(ast.String(), ['z', '\0'])
        )
        self._parse("true", "expr").should.be.equal(
            ast.ConstExpression(ast.Bool(), True)
        )
        self._parse("()", "expr").should.be.equal(
            ast.ConstExpression(ast.Unit(), None)
        )

    def test_constr(self):
        self._parse("Node", "constr").should.be.equal(
            ast.Constructor("Node", [])
        )
        self._parse("Node of int", "constr").should.be.equal(
            ast.Constructor("Node", [ast.Int()])
        )

    def test_simple_variable_def(self):
        foo_var = ast.VariableDef("foo")
        self._parse("mutable foo : int", "def").should.be.equal(
            ast.VariableDef("foo", ast.Ref(ast.Int()))
        )

        self._parse("mutable foo", "def").should.be.equal(foo_var)

    def test_array_variable_def(self):
        array_var = ast.ArrayVariableDef("foo", [TestParser.two])
        self._parse("mutable foo [2]", "def").should.be.equal(array_var)
        self._parse("mutable foo [2] : int", "def").should.be.equal(
            ast.ArrayVariableDef("foo", [TestParser.two], ast.Array(ast.Int()))
        )

    def test_while_expr(self):
        self._parse("while true do true done", "expr").should.be.equal(
            ast.WhileExpression(self.true, self.true)
        )

    def test_if_expr(self):
        self._parse("if true then true else true", "expr").should.be.equal(
            ast.IfExpression(self.true, self.true, self.true)
        )
        self._parse("if true then true", "expr").should.be.equal(
            ast.IfExpression(self.true, self.true)
        )

    def test_for_expr(self):
        self._parse("for i = 1 to 1 do true done", "expr").should.be.equal(
            ast.ForExpression(
                "i", TestParser.one, TestParser.one, self.true
            )
        )
        self._parse("for i = 1 downto 1 do true done", "expr").should.be.equal(
            ast.ForExpression(
                "i", TestParser.one, TestParser.one, self.true, True
            )
        )

    def test_pattern(self):
        self._parse("true", "pattern").should.be.equal(self.true)
        self._parse("Red true", "pattern").should.be.equal(
            ast.Pattern("Red", [self.true])
        )

    def test_simple_pattern_list(self):
        self._parse("", "simple_pattern_list").should.be.equal([])

    def test_regression_pattern_constructor_without_parens(self):
        raise unittest.SkipTest("re-enable me after bug #33 is fixed")

        pattern = ast.Pattern("Red", [])
        self._parse("Red Red", "simple_pattern_list").should.be.equal(
            [pattern, pattern]
        )

    def test_match_expr(self):
        self._parse(
            "match true with true -> true end", "expr"
        ).should.be.equal(
            ast.MatchExpression(self.true, [ast.Clause(self.true, self.true)])
        )

    def test_clause(self):
        self._parse("true -> true", "clause").should.be.equal(
            ast.Clause(self.true, self.true)
        )

    def test_clause_seq(self):
        clause = ast.Clause(self.true, self.true)

        self._parse("", "clause_seq").should.be.equal(None)
        self._parse(
            "true -> true | true -> true", "clause_seq"
        ).should.be.equal(
            [clause, clause]
        )

    def test_delete(self):
        self._parse("delete true", "expr").should.be.equal(
            ast.DeleteExpression(self.true)
        )

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
        self.assertTrue(
            isinstance(parsed, ast.UnaryExpression),
            "Unary operator '%s' failed to parse\
             as a unary expression"
            % operator
        )
        self.assertEqual(
            parsed.operator,
            operator,
            "Unary operator '%s' failed to parse;\
             instead, it is parsing as '%s'"
            % (operator, parsed.operator)
        )
        self.assertEqual(
            parsed.operand,
            TestParser.one,
            "Unary operator '%s' did not correctly\
             provide the value for its argument"
            % operator
        )

    def test_binary_expr(self):
        for operator in list(lex.binary_operators.keys()) + ["mod"]:
            self._check_binary_operator(operator)

    def test_unary_expr(self):
        for operator in list(lex.unary_operators.keys()) + ["not"]:
            self._check_unary_operator(operator)

    def test_begin_end_expr(self):
        self._parse("begin 1 end", "expr").should.be.equal(TestParser.one)

    def test_function_call_expr(self):
        self._parse("f 1", "expr").should.be.equal(
            ast.FunctionCallExpression("f", [TestParser.one])
        )

    def test_constructor_call_expr(self):
        self._parse("Red 1", "expr").should.be.equal(
            ast.ConstructorCallExpression("Red", [TestParser.one])
        )

    def test_simple_expr_seq(self):
        self._parse("", "simple_expr_seq").should.be.equal(None)
        self._parse("1", "simple_expr_seq").should.be.equal([TestParser.one])
        self._parse("1 2", "simple_expr_seq").should.be.equal(
            [TestParser.one, TestParser.two]
        )

    def test_dim_expr(self):
        dim = self._parse("dim name", "expr")

        self.assertTrue(isinstance(dim, ast.DimExpression))
        self.assertEqual(dim.name, "name")

        dim = self._parse("dim 2 name", "expr")

        self.assertTrue(isinstance(dim, ast.DimExpression))
        self.assertEqual(dim.name, "name")
        self.assertEqual(dim.dimension, 2)

    def test_in_expr(self):
        in_expr = ast.LetInExpression(TestParser.xfunc, TestParser.one)
        self._parse("let x = 1 in 1", "expr").should.be.equal(in_expr)

    def test_new(self):
        self._parse("new int", "expr").should.be.equal(
            ast.NewExpression(ast.Int())
        )

    def test_expr_comma_seq(self):
        self._parse("", "expr_comma_seq").should.be.equal(None)
        self._parse("1", "expr_comma_seq").should.be.equal([TestParser.one])
        self._parse("1, 2", "expr_comma_seq").should.be.equal(
            [TestParser.one, TestParser.two]
        )

    def test_array_expr(self):
        self._parse("a[1]", "expr").should.be.equal(
            ast.ArrayExpression("a", [TestParser.one])
        )

    def test_paren_expr(self):
        self._parse("(1)", "expr").should.be.equal(TestParser.one)

    def test_conid_expr(self):
        self._parse("Red", "expr").should.be.equal(ast.ConidExpression("Red"))

    def test_genid_expr(self):
        self._parse("f", "expr").should.be.equal(ast.GenidExpression("f"))

    def test_constr_pipe_seq(self):
        self._parse("", "constr_pipe_seq").should.be.equal(None)
        self._parse("Red | Green | Blue", "constr_pipe_seq").should.be.equal(
            [ast.Constructor("Red"),
             ast.Constructor("Green"),
             ast.Constructor("Blue")]
        )

    def test_tdef(self):
        self._parse("color = Red", "tdef").should.be.equal(
            ast.TDef(ast.User("color"), [ast.Constructor("Red")])
        )

        self._parse("int = Red", "tdef").should.be.equal(
            ast.TDef(ast.Int(), [ast.Constructor("Red")])
        )

    def test_tdef_and_seq(self):
        self._parse("", "tdef_and_seq").should.be.equal(None)
        self._parse(
            "color = Red and shoes = Slacks", "tdef_and_seq"
        ).should.be.equal(
            [
                ast.TDef(ast.User("color"), [ast.Constructor("Red")]),
                ast.TDef(ast.User("shoes"), [ast.Constructor("Slacks")])
            ]
        )

    def test_typedef(self):
        raise unittest.SkipTest(
            "re-enable me after simple_api branch gets merged"
        )

        self._parse("type color = Red", "typedef").should.be.equal(
            ast.TypeDefList(
                [
                    ast.TDef(
                        ast.User("color"),
                        [ast.Constructor("Red")]
                    )
                ]
            )
        )

    def test_type_seq(self):
        self._parse("", "type_seq").should.be.equal(None)
        self._parse("int int", "type_seq").should.be.equal(
            [ast.Int(), ast.Int()]
        )
