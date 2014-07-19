import unittest

import sure

from compiler import ast, error, lex, parse


class TestParser(unittest.TestCase):
    parsers = {}

    @classmethod
    def setUpClass(cls):
        cls.one = cls._parse("1", "expr")
        cls.two = cls._parse("2", "expr")
        cls.true = cls._parse("true", "expr")
        cls.false = cls._parse("false", "expr")

        cls.xfunc = cls._parse("let x = 1", "letdef")
        cls.yfunc = cls._parse("let y = 2", "letdef")

    @classmethod
    def _parse(cls, data, start='program'):
        mock = error.LoggerMock()

        # memoization
        try:
            parser = cls.parsers[start]
        except KeyError:
            parser = cls.parsers[start] = parse.Parser(
                logger=mock,
                optimize=False,
                start=start,
                debug=False
            )

        tree = parser.parse(data=data)

        return tree

    def test_parse(self):
        parse.parse("").should.equal(ast.Program([]))
        mock = error.LoggerMock()
        parse.parse("", logger=mock).should.equal(ast.Program([]))

    def test_empty_program(self):
        self._parse("").should.equal(ast.Program([]))

    def test_def_list(self):
        self._parse("", "def_list").should.equal([])

        self._parse("let x = 1", "def_list").should.equal([self.xfunc])

        self._parse("let x = 1 let y = 2", "def_list").should.equal(
            [self.xfunc, self.yfunc]
        )

    def test_letdef(self):
        self._parse("let x = 1", "letdef").should.equal(
            ast.LetDef(
                [ast.FunctionDef("x", [], self.one)]
            )
        )
        self._parse("let rec x = 1", "letdef").should.equal(
            ast.LetDef(
                [ast.FunctionDef("x", [], self.one)], True
            )
        )

    def test_function_def(self):
        self._parse("let x = 1", "def").should.equal(
            ast.FunctionDef("x", [], self.one)
        )

        self._parse("let x y (z:int) = 1", "def").should.equal(
            ast.FunctionDef(
                "x",
                [ast.Param("y"), ast.Param("z", ast.Int())],
                self.one
            )
        )

        self._parse("let x y z:int = 1", "def").should.equal(
            ast.FunctionDef(
                "x",
                [ast.Param("y"), ast.Param("z")], self.one, ast.Int()
            )
        )

    def test_param_list(self):
        self._parse("", "param_list").should.equal([])

        self._parse("my_param", "param_list").should.equal(
            [ast.Param("my_param")]
        )

        self._parse("a b", "param_list").should.equal(
            [ast.Param("a"), ast.Param("b")]
        )

    def test_param(self):
        self._parse("my_parameter", "param").should.equal(
            ast.Param("my_parameter")
        )
        self._parse("(my_parameter: int)", "param").should.equal(
            ast.Param("my_parameter", ast.Int())
        )
        self._parse("my_parameter: int", "param").should.be(None)

    def test_builtin_type(self):
        for type_name, type_node in ast.builtin_types_map.items():
            self._parse(type_name, "type").should.equal(type_node())

    def test_star_comma_seq(self):
        self._parse("*", "star_comma_seq").should.equal(1)
        self._parse("*, *, *", "star_comma_seq").should.equal(3)

    def test_array_type(self):
        array_node = ast.Array(ast.Int())
        self._parse("array of int", "type").should.equal(array_node)
        self._parse("array [*, *] of int", "type").should.equal(
            ast.Array(ast.Int(), 2)
        )

    def test_function_type(self):
        func_node = ast.Function(ast.Int(), ast.Float())
        self._parse("int -> float", "type").should.equal(func_node)

    def test_ref_type(self):
        ref_node = ast.Ref(ast.Int())
        self._parse("int ref", "type").should.equal(ref_node)

    def test_user_type(self):
        user_node = ast.User("mytype")
        self._parse("mytype", "type").should.equal(user_node)

    def test_type_paren(self):
        self._parse("(int)", "type").should.equal(ast.Int())

    def test_const(self):
        self._parse("5", "expr").should.equal(
            ast.ConstExpression(ast.Int(), 5)
        )
        self._parse("5.7", "expr").should.equal(
            ast.ConstExpression(ast.Float(), 5.7)
        )
        self._parse("'z'", "expr").should.equal(
            ast.ConstExpression(ast.Char(), 'z')
        )
        self._parse('"z"', "expr").should.equal(
            ast.ConstExpression(ast.String(), ['z', '\0'])
        )
        self._parse("true", "expr").should.equal(
            ast.ConstExpression(ast.Bool(), True)
        )
        self._parse("()", "expr").should.equal(
            ast.ConstExpression(ast.Unit(), None)
        )

    def test_constr(self):
        self._parse("Node", "constr").should.equal(
            ast.Constructor("Node", [])
        )
        self._parse("Node of int", "constr").should.equal(
            ast.Constructor("Node", [ast.Int()])
        )

    def test_simple_variable_def(self):
        foo_var = ast.VariableDef("foo")
        self._parse("mutable foo : int", "def").should.equal(
            ast.VariableDef("foo", ast.Ref(ast.Int()))
        )

        self._parse("mutable foo", "def").should.equal(foo_var)

    def test_array_variable_def(self):
        array_var = ast.ArrayVariableDef("foo", [self.two])
        self._parse("mutable foo [2]", "def").should.equal(array_var)
        self._parse("mutable foo [2] : int", "def").should.equal(
            ast.ArrayVariableDef("foo", [self.two], ast.Array(ast.Int()))
        )

    def test_while_expr(self):
        self._parse("while true do true done", "expr").should.equal(
            ast.WhileExpression(self.true, self.true)
        )

    def test_if_expr(self):
        self._parse("if true then true else true", "expr").should.equal(
            ast.IfExpression(self.true, self.true, self.true)
        )
        self._parse("if true then true", "expr").should.equal(
            ast.IfExpression(self.true, self.true)
        )

    def test_for_expr(self):
        self._parse("for i = 1 to 1 do true done", "expr").should.equal(
            ast.ForExpression(
                "i", self.one, self.one, self.true
            )
        )
        self._parse("for i = 1 downto 1 do true done", "expr").should.equal(
            ast.ForExpression(
                "i", self.one, self.one, self.true, True
            )
        )

    def test_pattern(self):
        self._parse("true", "pattern").should.equal(self.true)
        self._parse("Red true", "pattern").should.equal(
            ast.Pattern("Red", [self.true])
        )

    def test_simple_pattern_list(self):
        self._parse("", "simple_pattern_list").should.equal([])

    @unittest.skip("Enable me after bug #33 is fixed.")
    def test_regression_pattern_constructor_without_parens(self):
        pattern = ast.Pattern("Red", [])
        self._parse("Red Red", "simple_pattern_list").should.equal(
            [pattern, pattern]
        )

    def test_match_expr(self):
        self._parse(
            "match true with true -> true end", "expr"
        ).should.equal(
            ast.MatchExpression(self.true, [ast.Clause(self.true, self.true)])
        )

    def test_clause(self):
        self._parse("true -> true", "clause").should.equal(
            ast.Clause(self.true, self.true)
        )

    def test_clause_seq(self):
        clause1 = ast.Clause(self.one, self.two)
        clause2 = ast.Clause(self.true, self.false)

        self._parse("", "clause_seq").should.be(None)
        self._parse(
            "1 -> 2 | true -> false", "clause_seq"
        ).should.equal(
            [clause1, clause2]
        )

    def test_delete(self):
        self._parse("delete true", "expr").should.equal(
            ast.DeleteExpression(self.true)
        )

    def _check_binary_operator(self, operator):
        expr = "1 %s 2" % operator
        parsed = self._parse(expr, "expr")
        parsed.should.be.an(ast.BinaryExpression)
        (parsed.operator).should.equal(operator)
        (parsed.leftOperand).should.equal(self.one)
        (parsed.rightOperand).should.equal(self.two)

    def _check_unary_operator(self, operator):
        expr = "%s 1" % operator
        parsed = self._parse(expr, "expr")
        parsed.should.be.an(ast.UnaryExpression)
        (parsed.operator).should.equal(operator)
        (parsed.operand).should.equal(self.one)

    def test_binary_expr(self):
        for operator in list(lex.binary_operators.keys()) + ["mod"]:
            self._check_binary_operator(operator)

    def test_unary_expr(self):
        for operator in list(lex.unary_operators.keys()) + ["not"]:
            self._check_unary_operator(operator)

    def test_begin_end_expr(self):
        self._parse("begin 1 end", "expr").should.equal(self.one)

    def test_function_call_expr(self):
        self._parse("f 1", "expr").should.equal(
            ast.FunctionCallExpression("f", [self.one])
        )

    def test_constructor_call_expr(self):
        self._parse("Red 1", "expr").should.equal(
            ast.ConstructorCallExpression("Red", [self.one])
        )

    def test_simple_expr_seq(self):
        self._parse("", "simple_expr_seq").should.be(None)
        self._parse("1", "simple_expr_seq").should.equal([self.one])
        self._parse("1 2", "simple_expr_seq").should.equal(
            [self.one, self.two]
        )

    def test_dim_expr(self):
        parsed = self._parse("dim name", "expr")
        parsed.should.be.an(ast.DimExpression)
        (parsed.name).should.equal("name")

        parsed = self._parse("dim 2 name", "expr")
        parsed.should.be.an(ast.DimExpression)
        (parsed.name).should.equal("name")
        (parsed.dimension).should.equal(2)

    def test_in_expr(self):
        in_expr = ast.LetInExpression(self.xfunc, self.one)
        self._parse("let x = 1 in 1", "expr").should.equal(in_expr)

    def test_new(self):
        self._parse("new int", "expr").should.equal(
            ast.NewExpression(ast.Int())
        )

    def test_expr_comma_seq(self):
        self._parse("", "expr_comma_seq").should.be(None)
        self._parse("1", "expr_comma_seq").should.equal([self.one])
        self._parse("1, 2", "expr_comma_seq").should.equal(
            [self.one, self.two]
        )

    def test_array_expr(self):
        self._parse("a[1]", "expr").should.equal(
            ast.ArrayExpression("a", [self.one])
        )

    def test_paren_expr(self):
        self._parse("(1)", "expr").should.equal(self.one)

    def test_conid_expr(self):
        self._parse("Red", "expr").should.equal(ast.ConidExpression("Red"))

    def test_genid_expr(self):
        self._parse("f", "expr").should.equal(ast.GenidExpression("f"))

    def test_constr_pipe_seq(self):
        self._parse("", "constr_pipe_seq").should.be(None)
        self._parse("Red | Green | Blue", "constr_pipe_seq").should.equal(
            [ast.Constructor("Red"),
             ast.Constructor("Green"),
             ast.Constructor("Blue")]
        )

    def test_tdef(self):
        self._parse("color = Red", "tdef").should.equal(
            ast.TDef(ast.User("color"), [ast.Constructor("Red")])
        )

        self._parse("int = Red", "tdef").should.equal(
            ast.TDef(ast.Int(), [ast.Constructor("Red")])
        )

    def test_tdef_and_seq(self):
        self._parse("", "tdef_and_seq").should.be(None)
        self._parse(
            "color = Red and shoes = Slacks", "tdef_and_seq"
        ).should.equal(
            [
                ast.TDef(ast.User("color"), [ast.Constructor("Red")]),
                ast.TDef(ast.User("shoes"), [ast.Constructor("Slacks")])
            ]
        )

    @unittest.skip("Enable me after #25 is merged.")
    def test_typedef(self):
        self._parse("type color = Red", "typedef").should.equal(
            ast.TypeDefList(
                [ast.TDef(ast.User("color"), [ast.Constructor("Red")])]
            )
        )

    def test_type_seq(self):
        self._parse("", "type_seq").should.be(None)
        self._parse("int float", "type_seq").should.equal(
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
            #     self._parse(expr1, "expr"),
            #     self._parse(expr2, "expr"),
            #     "'%s' must equal '%s'" % (expr1, expr2)
            # )
            parsed1 = self._parse(expr1, start)
            parsed2 = self._parse(expr2, start)
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
            parsed1 = self._parse(expr1, start)
            parsed2 = self._parse(expr2, start)
            parsed1.shouldnt.equal(parsed2)

    def test_regression_new(self):
        self._assert_equivalent((
            ("!new int", "!(new int)"),
            ("f new int", "f (new int)"),
        ))

    def test_precedence_int(self):
        self._assert_equivalent((
            ("1 + 2 * 3", "1 + (2 * 3)"),
            ("1 - 2 / 3", "1 - (2 / 3)"),
            ("1 + 2 + 3", "(1 + 2) + 3"),
            ("1 - 2 - 3", "(1 - 2) - 3"),
            ("1 - 2 + 3", "(1 - 2) + 3"),
            ("1 * 2 * 3", "(1 * 2) * 3"),
            ("1 / 2 / 3", "(1 / 2) / 3"),
            ("1 / 2 * 3", "(1 / 2) * 3"),

            ("1 - 2 mod 3", "1 - (2 mod 3)"),
            ("1 mod 2 mod 3", "(1 mod 2) mod 3"),
        ))

    def test_precedence_float(self):
        self._assert_equivalent((
            ("1.0 +. 2.0 *. 3.0", "1.0 +. (2.0 *. 3.0)"),
            ("1.0 -. 2.0 *. 3.0", "1.0 -. (2.0 *. 3.0)"),
            ("1.0 +. 2.0 /. 3.0", "1.0 +. (2.0 /. 3.0)"),
            ("1.0 -. 2.0 /. 3.0", "1.0 -. (2.0 /. 3.0)"),
            ("1.0 +. 2.0 +. 3.0", "(1.0 +. 2.0) +. 3.0"),
            ("1.0 -. 2.0 -. 3.0", "(1.0 -. 2.0) -. 3.0"),
            ("1.0 -. 2.0 +. 3.0", "(1.0 -. 2.0) +. 3.0"),
            ("1.0 *. 2.0 *. 3.0", "(1.0 *. 2.0) *. 3.0"),
            ("1.0 /. 2.0 /. 3.0", "(1.0 /. 2.0) /. 3.0"),
            ("1.0 /. 2.0 *. 3.0", "(1.0 /. 2.0) *. 3.0"),

            ("-2 ** 4", "(-2) ** 4"),
            ("1 ** 2 ** 3", "1 ** (2 ** 3)"),
            ("1 ** 2 * 3", "(1 ** 2) * 3"),
            ("1 ** 2 / 3", "(1 ** 2) / 3"),
            ("1.0 ** 2.0 *. 3.0", "(1.0 ** 2.0) *. 3.0"),
            ("1.0 ** 2.0 /. 3.0", "(1.0 ** 2.0) /. 3.0"),
        ))

    def test_precedence_bool(self):
        self._assert_equivalent((
            ("a || b && c", "a || (b && c)"),
            ("not a || b", "(not a) || b"),
            ("not a && b", "(not a) && b"),
            ("a || b || c", "(a || b) || c"),
            ("a && b && c", "(a && b) && c"),

            ("a == b && c == d", "(a == b) && (c == d)"),
            ("a != b && c != d", "(a != b) && (c != d)"),
            ("a = b && c = d", "(a = b) && (c = d)"),
            ("a < b || c < d", "(a < b) || (c < d)"),
            ("a > b || c > d", "(a > b) || (c > d)"),
            ("a <= b && c <> d", "(a <= b) && (c <> d)"),
            ("a >= b && c <> d", "(a >= b) && (c <> d)"),
        ))

    def test_precedence_rest(self):
        self._assert_equivalent((
            # function and constructor calls
            ("f 1 + 2", "(f 1) + 2"),
            ("F 1 + 2", "(F 1) + 2"),

            ("x + y[1]", "x + (y[1])"),
            ("!a[1]", "!(a[1])"),
            ("!f x", "(!f) x"),
            ("not f x", "not (f x)"),
            ("delete f x", "delete (f x)"),
            ("not F x", "not (F x)"),
            ("delete F x", "delete (F x)"),

            ("1 + 1 = 2", "(1 + 1) = 2"),
            ("x := a && b", "x := (a && b)"),
            ("x := 1 + 1", "x := (1 + 1)"),

            ("if p then if q then a else b", "if p then (if q then a else b)"),
            ("if p then 1 else 1 + 1", "if p then 1 else (1 + 1)"),
            (
                "if p then 1 else 2; if q then 1 else 2",
                "(if p then 1 else 2); (if q then 1 else 2)"
            ),
            (
                "let x = 5 in x; let y = 5 in y",
                "let x = 5 in (x; let y = 5 in y)"
            ),

            ("x; y; z", "(x; y); z"),
        ))

    def test_precedence_non_equiv(self):
        self._assert_non_equivalent("f -2", "f (-2)")

    def test_precedence_type(self):
        self._assert_equivalent((
            ("int -> int -> int", "int -> (int -> int)"),
            ("int ref ref", "(int ref) ref"),
            ("array of int -> int", "(array of int) -> int"),
        ), None, "type")

    def test_regression_precedence_func_ref(self):
        self._assert_equivalent("int -> int ref", "int -> (int ref)", "type")

    def test_regression_precedence_type_array_ref(self):
        self._assert_equivalent(
            "array of int ref",
            "array of (int ref)",
            'type'
        )
