import unittest

from compiler import ast, error, lex, parse


class TestModuleAPI(unittest.TestCase):
    """Test the API of the parse module."""

    def test_parse(self):
        p1 = parse.Parser()
        parse.parse("").should.equal(p1.parse(""))

        mock = error.LoggerMock()
        p2 = parse.Parser(logger=mock)
        parse.parse("", logger=mock).should.equal(p2.parse(""))

        p3 = parse.Parser(start="type")
        parse.parse("int", start="type").should.equal(p3.parse("int"))

    def test_quiet_parse(self):
        mock = error.LoggerMock()
        p1 = parse.Parser(logger=mock)
        (parse.quiet_parse("")).should.equal(p1.parse(""))

        p2 = parse.Parser(start='type')
        (parse.quiet_parse("int", start='type')).should.equal(p2.parse("int"))


class TestParserAPI(unittest.TestCase):
    """Test the API of the Parser class."""

    @classmethod
    def setUpClass(cls):
        cls.one = parse.quiet_parse("1", "expr")
        cls.two = parse.quiet_parse("2", "expr")
        cls.true = parse.quiet_parse("true", "expr")
        cls.false = parse.quiet_parse("false", "expr")
        cls.unit = parse.quiet_parse("()", "expr")

        cls.xfunc = parse.quiet_parse("let x = 1", "letdef")
        cls.yfunc = parse.quiet_parse("let y = 2", "letdef")

    def test_empty_program(self):
        parse.quiet_parse("").should.equal(ast.Program([]))

    def test_def_list(self):
        parse.quiet_parse("", "def_list").should.equal([])

        parse.quiet_parse("let x = 1", "def_list").should.equal([self.xfunc])

        parse.quiet_parse("let x = 1 let y = 2", "def_list").should.equal(
            [self.xfunc, self.yfunc]
        )

    def test_letdef(self):
        parse.quiet_parse("let x = 1", "letdef").should.equal(
            ast.LetDef(
                [ast.FunctionDef("x", [], self.one)]
            )
        )
        parse.quiet_parse("let rec x = 1", "letdef").should.equal(
            ast.LetDef(
                [ast.FunctionDef("x", [], self.one)], True
            )
        )

    def test_function_def(self):
        parse.quiet_parse("let x = 1", "def").should.equal(
            ast.FunctionDef("x", [], self.one)
        )

        parse.quiet_parse("let x y (z:int) = 1", "def").should.equal(
            ast.FunctionDef(
                "x",
                [ast.Param("y"), ast.Param("z", ast.Int())],
                self.one
            )
        )

        parse.quiet_parse("let x y z:int = 1", "def").should.equal(
            ast.FunctionDef(
                "x",
                [ast.Param("y"), ast.Param("z")], self.one, ast.Int()
            )
        )

    def test_param_list(self):
        parse.quiet_parse("", "param_list").should.equal([])

        parse.quiet_parse("my_param", "param_list").should.equal(
            [ast.Param("my_param")]
        )

        parse.quiet_parse("a b", "param_list").should.equal(
            [ast.Param("a"), ast.Param("b")]
        )

    def test_param(self):
        parse.quiet_parse("my_parameter", "param").should.equal(
            ast.Param("my_parameter")
        )
        parse.quiet_parse("(my_parameter: int)", "param").should.equal(
            ast.Param("my_parameter", ast.Int())
        )

        self._assert_parse_fails("my_parameter: int", "param")

    def test_builtin_type(self):
        for name, typecon in ast.builtin_types_map.items():
            parse.quiet_parse(name, "type").should.equal(typecon())

    def test_star_comma_seq(self):
        parse.quiet_parse("*", "star_comma_seq").should.equal(1)
        parse.quiet_parse("*, *, *", "star_comma_seq").should.equal(3)

    def test_array_type(self):
        array_node = ast.Array(ast.Int())
        parse.quiet_parse("array of int", "type").should.equal(array_node)
        parse.quiet_parse("array [*, *] of int", "type").should.equal(
            ast.Array(ast.Int(), 2)
        )

    def test_function_type(self):
        func_node = ast.Function(ast.Int(), ast.Float())
        parse.quiet_parse("int -> float", "type").should.equal(func_node)

    def test_ref_type(self):
        ref_node = ast.Ref(ast.Int())
        parse.quiet_parse("int ref", "type").should.equal(ref_node)

    def test_user_type(self):
        user_node = ast.User("mytype")
        parse.quiet_parse("mytype", "type").should.equal(user_node)

    def test_type_paren(self):
        parse.quiet_parse("(int)", "type").should.equal(ast.Int())

    def test_const(self):
        parse.quiet_parse("5", "expr").should.equal(
            ast.ConstExpression(ast.Int(), 5)
        )
        parse.quiet_parse("5.7", "expr").should.equal(
            ast.ConstExpression(ast.Float(), 5.7)
        )
        parse.quiet_parse("'z'", "expr").should.equal(
            ast.ConstExpression(ast.Char(), "z")
        )
        parse.quiet_parse('"z"', "expr").should.equal(
            ast.ConstExpression(ast.String(), ["z", '\0'])
        )
        parse.quiet_parse("true", "expr").should.equal(
            ast.ConstExpression(ast.Bool(), True)
        )
        parse.quiet_parse("()", "expr").should.equal(
            ast.ConstExpression(ast.Unit(), None)
        )

    def test_constr(self):
        parse.quiet_parse("Node", "constr").should.equal(
            ast.Constructor("Node", [])
        )
        parse.quiet_parse("Node of int", "constr").should.equal(
            ast.Constructor("Node", [ast.Int()])
        )

    def test_simple_variable_def(self):
        foo_var = ast.VariableDef("foo")
        parse.quiet_parse("mutable foo : int", "def").should.equal(
            ast.VariableDef("foo", ast.Ref(ast.Int()))
        )

        parse.quiet_parse("mutable foo", "def").should.equal(foo_var)

    def test_array_variable_def(self):
        array_var = ast.ArrayVariableDef("foo", [self.two])
        parse.quiet_parse("mutable foo [2]", "def").should.equal(array_var)
        parse.quiet_parse("mutable foo [2] : int", "def").should.equal(
            ast.ArrayVariableDef("foo", [self.two], ast.Array(ast.Int()))
        )

    def test_while_expr(self):
        parse.quiet_parse("while true do () done", "expr").should.equal(
            ast.WhileExpression(self.true, self.unit)
        )

    def test_if_expr(self):
        parse.quiet_parse("if true then 1 else 2", "expr").should.equal(
            ast.IfExpression(self.true, self.one, self.two)
        )
        parse.quiet_parse("if true then ()", "expr").should.equal(
            ast.IfExpression(self.true, self.unit)
        )

    def test_for_expr(self):
        parse.quiet_parse("for i = 1 to 2 do () done", "expr").should.equal(
            ast.ForExpression(
                "i", self.one, self.two, self.unit
            )
        )
        parse.quiet_parse("for i = 2 downto 1 do () done", "expr").should.equal(
            ast.ForExpression(
                "i", self.two, self.one, self.unit, True
            )
        )

    def test_pattern(self):
        parse.quiet_parse("true", "pattern").should.equal(self.true)
        parse.quiet_parse("Red true", "pattern").should.equal(
            ast.Pattern("Red", [self.true])
        )
        parse.quiet_parse("(true)", "pattern").should.equal(self.true)

        parse.quiet_parse("foo", "pattern").should.equal(ast.GenidPattern("foo"))
        parse.quiet_parse("true", "pattern").should.equal(self.true)
        parse.quiet_parse("false", "pattern").should.equal(self.false)
        parse.quiet_parse("'c'", "pattern").should.equal(
            ast.ConstExpression(ast.Char(), "c")
        )
        parse.quiet_parse("42.0", "pattern").should.equal(
            ast.ConstExpression(ast.Float(), 42.0)
        )
        parse.quiet_parse("+.42.0", "pattern").should.equal(
            ast.ConstExpression(ast.Float(), 42.0)
        )
        parse.quiet_parse("-.42.0", "pattern").should.equal(
            ast.ConstExpression(ast.Float(), -42.0)
        )
        parse.quiet_parse("42", "pattern").should.equal(
            ast.ConstExpression(ast.Int(), 42)
        )
        parse.quiet_parse("+42", "pattern").should.equal(
            ast.ConstExpression(ast.Int(), 42)
        )
        parse.quiet_parse("-42", "pattern").should.equal(
            ast.ConstExpression(ast.Int(), -42)
        )

    def test_simple_pattern_seq(self):
        self._assert_parse_fails("", "simple_pattern_seq")
        red, blue = ast.Pattern("Red"), ast.Pattern("Blue")
        parse.quiet_parse("Red", "simple_pattern_seq").should.equal([red])
        parse.quiet_parse("Red Blue", "simple_pattern_seq").should.equal(
            [red, blue]
        )

    def test_match_expr(self):
        parse.quiet_parse(
            "match true with false -> 1 end", "expr"
        ).should.equal(
            ast.MatchExpression(self.true, [ast.Clause(self.false, self.one)])
        )

    def test_clause(self):
        parse.quiet_parse("true -> false", "clause").should.equal(
            ast.Clause(self.true, self.false)
        )

    def test_clause_seq(self):
        clause1 = ast.Clause(self.one, self.two)
        clause2 = ast.Clause(self.true, self.false)

        parse.quiet_parse(
            "1 -> 2 | true -> false", "clause_seq"
        ).should.equal(
            [clause1, clause2]
        )

        self._assert_parse_fails("", "clause_seq")

    def test_delete(self):
        parse.quiet_parse("delete p", "expr").should.equal(
            ast.DeleteExpression(
                ast.GenidExpression("p")
            )
        )

    def _check_binary_operator(self, operator):
        expr = "1 %s 2" % operator
        parsed = parse.quiet_parse(expr, "expr")
        parsed.should.be.an(ast.BinaryExpression)
        parsed.operator.should.equal(operator)
        parsed.leftOperand.should.equal(self.one)
        parsed.rightOperand.should.equal(self.two)

    def _check_unary_operator(self, operator):
        expr = "%s 1" % operator
        parsed = parse.quiet_parse(expr, "expr")
        parsed.should.be.an(ast.UnaryExpression)
        parsed.operator.should.equal(operator)
        parsed.operand.should.equal(self.one)

    def test_binary_expr(self):
        for operator in list(lex.binary_operators.keys()) + ["mod"]:
            self._check_binary_operator(operator)

    def test_unary_expr(self):
        for operator in list(lex.unary_operators.keys()) + ["not"]:
            self._check_unary_operator(operator)

    def test_begin_end_expr(self):
        parse.quiet_parse("begin 1 end", "expr").should.equal(self.one)

    def test_function_call_expr(self):
        parse.quiet_parse("f 1", "expr").should.equal(
            ast.FunctionCallExpression("f", [self.one])
        )

    def test_constructor_call_expr(self):
        parse.quiet_parse("Red 1", "expr").should.equal(
            ast.ConstructorCallExpression("Red", [self.one])
        )

    def test_simple_expr_seq(self):
        self._assert_parse_fails("", "simple_expr_seq")

        parse.quiet_parse("1", "simple_expr_seq").should.equal([self.one])
        parse.quiet_parse("1 2", "simple_expr_seq").should.equal(
            [self.one, self.two]
        )

    def test_dim_expr(self):
        parsed = parse.quiet_parse("dim name", "expr")
        parsed.should.be.an(ast.DimExpression)
        parsed.name.should.equal("name")

        parsed = parse.quiet_parse("dim 2 name", "expr")
        parsed.should.be.an(ast.DimExpression)
        parsed.name.should.equal("name")
        parsed.dimension.should.equal(2)

    def test_in_expr(self):
        in_expr = ast.LetInExpression(self.xfunc, self.one)
        parse.quiet_parse("let x = 1 in 1", "expr").should.equal(in_expr)

    def test_new(self):
        parse.quiet_parse("new int", "expr").should.equal(
            ast.NewExpression(ast.Int())
        )

    def test_expr_comma_seq(self):
        self._assert_parse_fails("", "expr_comma_seq")

        parse.quiet_parse("1", "expr_comma_seq").should.equal([self.one])
        parse.quiet_parse("1, 2", "expr_comma_seq").should.equal(
            [self.one, self.two]
        )

    def test_array_expr(self):
        parse.quiet_parse("a[1]", "expr").should.equal(
            ast.ArrayExpression("a", [self.one])
        )

    def test_paren_expr(self):
        parse.quiet_parse("(1)", "expr").should.equal(self.one)

    def test_conid_expr(self):
        parse.quiet_parse("Red", "expr").should.equal(ast.ConidExpression("Red"))

    def test_genid_expr(self):
        parse.quiet_parse("f", "expr").should.equal(ast.GenidExpression("f"))

    def test_constr_pipe_seq(self):
        self._assert_parse_fails("", "constr_pipe_seq")

        parse.quiet_parse("Red | Green | Blue", "constr_pipe_seq").should.equal(
            [ast.Constructor("Red"),
             ast.Constructor("Green"),
             ast.Constructor("Blue")]
        )

    def test_tdef(self):
        parse.quiet_parse("color = Red", "tdef").should.equal(
            ast.TDef(ast.User("color"), [ast.Constructor("Red")])
        )

        parse.quiet_parse("int = Red", "tdef").should.equal(
            ast.TDef(ast.Int(), [ast.Constructor("Red")])
        )

    def test_tdef_and_seq(self):
        self._assert_parse_fails("", "tdef_and_seq")

        parse.quiet_parse(
            "color = Red and shoes = Slacks", "tdef_and_seq"
        ).should.equal(
            [
                ast.TDef(ast.User("color"), [ast.Constructor("Red")]),
                ast.TDef(ast.User("shoes"), [ast.Constructor("Slacks")])
            ]
        )

    def test_typedef(self):
        parse.quiet_parse("type color = Red", "typedef").should.equal(
            [ast.TDef(ast.User("color"), [ast.Constructor("Red")])]
        )

    def test_type_seq(self):
        self._assert_parse_fails("", "type_seq")

        parse.quiet_parse("int float", "type_seq").should.equal(
            [ast.Int(), ast.Float()]
        )

    def _assert_equivalent(self, expr1, expr2=None, start="expr"):
        """
        Assert that two expressions are parsed into equivalent ASTs.
        You can pass either two expressions (expr1, expr2) or a sequence
        of expression tuples as expr1, leaving expr2 to None.
        """

        if expr2 is None:
            # sequence of expressions
            exprs = expr1
            for expr1, expr2 in exprs:
                self._assert_equivalent(expr1, expr2, start)
        else:
            # self.assertEqual(
            #     parse.quiet_parse(expr1, "expr"),
            #     parse.quiet_parse(expr2, "expr"),
            #     "'%s' must equal '%s'" % (expr1, expr2)
            # )
            parsed1 = parse.quiet_parse(expr1, start)
            parsed2 = parse.quiet_parse(expr2, start)
            parsed1.should.equal(parsed2)

    def _assert_non_equivalent(self, expr1, expr2=None, start="expr"):
        """
        Assert that two expressions are not parsed as equivalent ASTs.
        The API is similar to _assert_equivalent.
        """

        if expr2 is None:
            # sequence of expressions
            exprs = expr1
            for expr1, expr2 in exprs:
                self._assert_non_equivalent(expr1, expr2, start)
        else:
            parsed1 = parse.quiet_parse(expr1, start)
            parsed2 = parse.quiet_parse(expr2, start)
            parsed1.shouldnt.equal(parsed2)

    def _assert_parse_fails(self, expr, start="expr"):
        """
        Assert that attempting to parse the expression from the given
        start will fail.
        """
        p = parse.Parser(logger=error.LoggerMock(), start=start)
        p.parse(expr)
        p.logger.success.should.be.false

    def test_precedence_new_bang(self):
        self._assert_equivalent("!new int", "!(new int)")

    def test_precedence_arrayexpr_bang(self):
        self._assert_equivalent("!a[0]", "!(a[0])")

    def test_precedence_bang_juxtaposition(self):
        self._assert_equivalent((
            ("!f x", "(!f) x"),
            ("!F x", "(!F) x")
        ))

    def test_precedence_juxtaposition_sign(self):
        self._assert_equivalent((
            ("+ f x", "+ (f x)"),
            ("+ F x", "+ (F x)"),

            ("- f x", "- (f x)"),
            ("- F x", "- (F x)"),

            ("+. f x", "+. (f x)"),
            ("+. F x", "+. (F x)"),

            ("-. f x", "-. (f x)"),
            ("-. F x", "-. (F x)"),

            ("not f x", "not (f x)"),
            ("not F x", "not (F x)"),

            ("delete f x", "delete (f x)"),
            ("delete F x", "delete (F x)")
        ))

    def test_precedence_sign_pow(self):
        self._assert_equivalent((
            ("+1 ** 2", "(+1) ** 2"),
            ("1 ** +2", "1 ** (+2)"),

            ("-1 ** 2", "(-1) ** 2"),
            ("1 ** -2", "1 ** (-2)"),

            ("+.1 ** 2", "(+.1) ** 2"),
            ("1 ** +.2", "1 ** (+.2)"),

            ("-.1 ** 2", "(-.1) ** 2"),
            ("1 ** -.2", "1 ** (-.2)"),

            ("not true ** 2", "(not true) ** 2"),
            ("1 ** not false", "1 ** (not false)"),

            ("delete p ** 2", "(delete p) ** 2"),
            ("1 ** delete p", "1 ** (delete p)"),
        ))

    def test_precedence_pow_multiplicative(self):
        self._assert_equivalent((
            ("1 ** 2 * 3", "(1 ** 2) * 3"),
            ("1 * 2 ** 3", "1 * (2 ** 3)"),

            ("1 ** 2 / 3", "(1 ** 2) / 3"),
            ("1 / 2 ** 3", "1 / (2 ** 3)"),

            ("1 ** 2 *. 3", "(1 ** 2) *. 3"),
            ("1 *. 2 ** 3", "1 *. (2 ** 3)"),

            ("1 ** 2 /. 3", "(1 ** 2) /. 3"),
            ("1 /. 2 ** 3", "1 /. (2 ** 3)"),

            ("1 ** 2 mod 3", "(1 ** 2) mod 3"),
            ("1 mod 2 ** 3", "1 mod (2 ** 3)"),
        ))

    def test_precedence_multiplicative_additive(self):
        self._assert_equivalent((
            ("1 + 2 * 3", "1 + (2 * 3)"),
            ("1 * 2 + 3", "(1 * 2) + 3"),
            ("1 + 2 / 3", "1 + (2 / 3)"),
            ("1 / 2 + 3", "(1 / 2) + 3"),
            ("1 + 2 *. 3", "1 + (2 *. 3)"),
            ("1 *. 2 + 3", "(1 *. 2) + 3"),
            ("1 + 2 /. 3", "1 + (2 /. 3)"),
            ("1 /. 2 + 3", "(1 /. 2) + 3"),
            ("1 + 2 mod 3", "1 + (2 mod 3)"),
            ("1 mod 2 + 3", "(1 mod 2) + 3"),

            ("1 - 2 * 3", "1 - (2 * 3)"),
            ("1 * 2 - 3", "(1 * 2) - 3"),
            ("1 - 2 / 3", "1 - (2 / 3)"),
            ("1 / 2 - 3", "(1 / 2) - 3"),
            ("1 - 2 *. 3", "1 - (2 *. 3)"),
            ("1 *. 2 - 3", "(1 *. 2) - 3"),
            ("1 - 2 /. 3", "1 - (2 /. 3)"),
            ("1 /. 2 - 3", "(1 /. 2) - 3"),
            ("1 - 2 mod 3", "1 - (2 mod 3)"),
            ("1 mod 2 - 3", "(1 mod 2) - 3"),

            ("1 +. 2 * 3", "1 +. (2 * 3)"),
            ("1 * 2 +. 3", "(1 * 2) +. 3"),
            ("1 +. 2 / 3", "1 +. (2 / 3)"),
            ("1 / 2 +. 3", "(1 / 2) +. 3"),
            ("1 +. 2 *. 3", "1 +. (2 *. 3)"),
            ("1 *. 2 +. 3", "(1 *. 2) +. 3"),
            ("1 +. 2 /. 3", "1 +. (2 /. 3)"),
            ("1 /. 2 +. 3", "(1 /. 2) +. 3"),
            ("1 +. 2 mod 3", "1 +. (2 mod 3)"),
            ("1 mod 2 +. 3", "(1 mod 2) +. 3"),

            ("1 -. 2 * 3", "1 -. (2 * 3)"),
            ("1 * 2 -. 3", "(1 * 2) -. 3"),
            ("1 -. 2 / 3", "1 -. (2 / 3)"),
            ("1 / 2 -. 3", "(1 / 2) -. 3"),
            ("1 -. 2 *. 3", "1 -. (2 *. 3)"),
            ("1 *. 2 -. 3", "(1 *. 2) -. 3"),
            ("1 -. 2 /. 3", "1 -. (2 /. 3)"),
            ("1 /. 2 -. 3", "(1 /. 2) -. 3"),
            ("1 -. 2 mod 3", "1 -. (2 mod 3)"),
            ("1 mod 2 -. 3", "(1 mod 2) -. 3")
        ))

    def test_precedence_additive_commparison(self):
        self._assert_equivalent((
            ("a + b = c", "(a + b) = c"),
            ("a = b + c", "a = (b + c)"),
            ("a - b = c", "(a - b) = c"),
            ("a = b - c", "a = (b - c)"),
            ("a +. b = c", "(a +. b) = c"),
            ("a = b +. c", "a = (b +. c)"),
            ("a -. b = c", "(a -. b) = c"),
            ("a = b -. c", "a = (b -. c)"),

            ("a + b <> c", "(a + b) <> c"),
            ("a <> b + c", "a <> (b + c)"),
            ("a - b <> c", "(a - b) <> c"),
            ("a <> b - c", "a <> (b - c)"),
            ("a +. b <> c", "(a +. b) <> c"),
            ("a <> b +. c", "a <> (b +. c)"),
            ("a -. b <> c", "(a -. b) <> c"),
            ("a <> b -. c", "a <> (b -. c)"),

            ("a + b > c", "(a + b) > c"),
            ("a > b + c", "a > (b + c)"),
            ("a - b > c", "(a - b) > c"),
            ("a > b - c", "a > (b - c)"),
            ("a +. b > c", "(a +. b) > c"),
            ("a > b +. c", "a > (b +. c)"),
            ("a -. b > c", "(a -. b) > c"),
            ("a > b -. c", "a > (b -. c)"),

            ("a + b < c", "(a + b) < c"),
            ("a < b + c", "a < (b + c)"),
            ("a - b < c", "(a - b) < c"),
            ("a < b - c", "a < (b - c)"),
            ("a +. b < c", "(a +. b) < c"),
            ("a < b +. c", "a < (b +. c)"),
            ("a -. b < c", "(a -. b) < c"),
            ("a < b -. c", "a < (b -. c)"),

            ("a + b <= c", "(a + b) <= c"),
            ("a <= b + c", "a <= (b + c)"),
            ("a - b <= c", "(a - b) <= c"),
            ("a <= b - c", "a <= (b - c)"),
            ("a +. b <= c", "(a +. b) <= c"),
            ("a <= b +. c", "a <= (b +. c)"),
            ("a -. b <= c", "(a -. b) <= c"),
            ("a <= b -. c", "a <= (b -. c)"),

            ("a + b >= c", "(a + b) >= c"),
            ("a >= b + c", "a >= (b + c)"),
            ("a - b >= c", "(a - b) >= c"),
            ("a >= b - c", "a >= (b - c)"),
            ("a +. b >= c", "(a +. b) >= c"),
            ("a >= b +. c", "a >= (b +. c)"),
            ("a -. b >= c", "(a -. b) >= c"),
            ("a >= b -. c", "a >= (b -. c)"),

            ("a + b == c", "(a + b) == c"),
            ("a == b + c", "a == (b + c)"),
            ("a - b == c", "(a - b) == c"),
            ("a == b - c", "a == (b - c)"),
            ("a +. b == c", "(a +. b) == c"),
            ("a == b +. c", "a == (b +. c)"),
            ("a -. b == c", "(a -. b) == c"),
            ("a == b -. c", "a == (b -. c)"),

            ("a + b != c", "(a + b) != c"),
            ("a != b + c", "a != (b + c)"),
            ("a - b != c", "(a - b) != c"),
            ("a != b - c", "a != (b - c)"),
            ("a +. b != c", "(a +. b) != c"),
            ("a != b +. c", "a != (b +. c)"),
            ("a -. b != c", "(a -. b) != c"),
            ("a != b -. c", "a != (b -. c)"),
        ))

    def test_precedence_comparison_band(self):
        self._assert_equivalent((
            ("a && b = c", "a && (b = c)"),
            ("a = b && c", "(a = b) && c"),

            ("a && b <> c", "a && (b <> c)"),
            ("a <> b && c", "(a <> b) && c"),

            ("a && b > c", "a && (b > c)"),
            ("a > b && c", "(a > b) && c"),

            ("a && b < c", "a && (b < c)"),
            ("a < b && c", "(a < b) && c"),

            ("a && b <= c", "a && (b <= c)"),
            ("a <= b && c", "(a <= b) && c"),

            ("a && b >= c", "a && (b >= c)"),
            ("a >= b && c", "(a >= b) && c"),

            ("a && b == c", "a && (b == c)"),
            ("a == b && c", "(a == b) && c"),

            ("a && b != c", "a && (b != c)"),
            ("a != b && c", "(a != b) && c"),
        ))

    def test_precedence_band_bor(self):
        self._assert_equivalent((
            ("a || b && c", "a || (b && c)"),
            ("a && b || c", "(a && b) || c"),
        ))

    def test_precedence_bor_assign(self):
        self._assert_equivalent((
            ("a := b || c", "a := (b || c)"),
            ("a || b := c", "(a || b) := c"),
        ))

    def test_precedence_assign_ifthenelse(self):
        self._assert_equivalent((
            ("if p then () else a := b", "if p then () else (a := b)"),
            ("if p then a := b", "if p then (a := b)"),
        ))

    def test_precedence_ifthenelse_semicolon(self):
        self._assert_equivalent((
            ("if p then 1 else 2; 3", "(if p then 1 else 2); 3"),
            ("if p then 2; 3", "(if p then 2); 3"),
        ))

    def test_precedence_assign_semicolon(self):
        self._assert_equivalent((
            ("a := b; c", "(a := b); c"),
            ("a; b := c", "a; (b := c)"),
        ))

    def test_precedence_semicolon_letin(self):
        self._assert_equivalent("let x = 0 in y; z", "let x = 0 in (y; z)")

    def test_associativity_arrayexpr(self):
        self._assert_parse_fails("a[0][0]")

    def test_associativity_pow(self):
        self._assert_equivalent("1 ** 2 ** 3", "1 ** (2 ** 3)")

    def test_associativity_multiplicative(self):
        self._assert_equivalent((
            ("1 * 2 * 3", "(1 * 2) * 3"),
            ("1 * 2 / 3", "(1 * 2) / 3"),
            ("1 * 2 *. 3", "(1 * 2) *. 3"),
            ("1 * 2 /. 3", "(1 * 2) /. 3"),

            ("1 / 2 * 3", "(1 / 2) * 3"),
            ("1 / 2 / 3", "(1 / 2) / 3"),
            ("1 / 2 *. 3", "(1 / 2) *. 3"),
            ("1 / 2 /. 3", "(1 / 2) /. 3"),

            ("1 *. 2 * 3", "(1 *. 2) * 3"),
            ("1 *. 2 / 3", "(1 *. 2) / 3"),
            ("1 *. 2 *. 3", "(1 *. 2) *. 3"),
            ("1 *. 2 /. 3", "(1 *. 2) /. 3"),

            ("1 /. 2 * 3", "(1 /. 2) * 3"),
            ("1 /. 2 / 3", "(1 /. 2) / 3"),
            ("1 /. 2 *. 3", "(1 /. 2) *. 3"),
            ("1 /. 2 /. 3", "(1 /. 2) /. 3"),

            ("1 mod 2 * 3", "(1 mod 2) * 3"),
            ("1 mod 2 / 3", "(1 mod 2) / 3"),
            ("1 mod 2 *. 3", "(1 mod 2) *. 3"),
            ("1 mod 2 /. 3", "(1 mod 2) /. 3")
        ))

    def test_associativity_additive(self):
        self._assert_equivalent((
            ("1 + 2 + 3", "(1 + 2) + 3"),
            ("1 + 2 - 3", "(1 + 2) - 3"),
            ("1 + 2 +. 3", "(1 + 2) +. 3"),
            ("1 + 2 -. 3", "(1 + 2) -. 3"),

            ("1 - 2 + 3", "(1 - 2) + 3"),
            ("1 - 2 - 3", "(1 - 2) - 3"),
            ("1 - 2 +. 3", "(1 - 2) +. 3"),
            ("1 - 2 -. 3", "(1 - 2) -. 3"),

            ("1 +. 2 + 3", "(1 +. 2) + 3"),
            ("1 +. 2 - 3", "(1 +. 2) - 3"),
            ("1 +. 2 +. 3", "(1 +. 2) +. 3"),
            ("1 +. 2 -. 3", "(1 +. 2) -. 3"),

            ("1 -. 2 + 3", "(1 -. 2) + 3"),
            ("1 -. 2 - 3", "(1 -. 2) - 3"),
            ("1 -. 2 +. 3", "(1 -. 2) +. 3"),
            ("1 -. 2 -. 3", "(1 -. 2) -. 3")
        ))

    def test_associativity_compariosn(self):
        self._assert_parse_fails("a = b = c")
        self._assert_parse_fails("a <> b <> c")
        self._assert_parse_fails("a > b > c")
        self._assert_parse_fails("a < b < c")
        self._assert_parse_fails("a <= b <= c")
        self._assert_parse_fails("a >= b >= c")
        self._assert_parse_fails("a == b == c")
        self._assert_parse_fails("a != b != c")

    def test_associativity_band(self):
        self._assert_equivalent("a && b && c", "(a && b) && c")

    def test_associativity_bor(self):
        self._assert_equivalent("a || b || c", "(a || b) || c")

    def test_associativity_assign(self):
        self._assert_parse_fails("a := b := c")

    def test_associativity_ifthenelse(self):
        self._assert_equivalent(
            "if p then if q then a else b",
            "if p then (if q then a else b)"
        )

    def test_associativity_semicolon(self):
        self._assert_equivalent("x; y; z", "(x; y); z")

    def test_precedence_non_equiv(self):
        self._assert_non_equivalent("f -2", "f (-2)")

    def test_precedence_array_ref(self):
        self._assert_equivalent(
            "array of int ref",
            "array of (int ref)",
            start="type"
        )

    def test_precedence_array_func(self):
        self._assert_equivalent(
            "array of int -> int",
            "(array of int) -> int",
            start="type"
        )

    def test_precedence_func_ref(self):
        self._assert_equivalent(
            "int -> int ref",
            "int -> (int ref)",
            start="type"
        )

    # NOTE: Test for array associativity deliberately ommitted,
    # as an array of array is considered an error in semantics, not syntax.

    def test_associativity_ref(self):
        self._assert_equivalent(
            "int ref ref",
            "(int ref) ref",
            start="type"
        )

    def test_associativity_func(self):
        self._assert_equivalent(
            "int -> int -> int",
            "int -> (int -> int)",
            start="type"
        )
