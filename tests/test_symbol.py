import unittest

from compiler import ast, symbol


class TestSymbolTableAPI(unittest.TestCase):
    """Test the API of the SymbolTable class."""

    @staticmethod
    def test_scope_init():
        scope = symbol.Scope([], True, 1)
        scope.should.have.property("entries").equal([])
        scope.should.have.property("visible").equal(True)
        scope.should.have.property("nesting").being(1)

    @staticmethod
    def test_symboltable_init():
        symbol.SymbolTable()

    @staticmethod
    def test_redef_identifier_error():
        exc = symbol.RedefIdentifierError
        issubclass(exc, symbol.SymbolError).should.be.true

    def test_functionality(self):
        expr = ast.GenidExpression("foo")
        expr.lineno, expr.lexpos = 1, 2
        param = ast.Param("foo")
        param.lineno, param.lexpos = 3, 4

        table = symbol.SymbolTable()
        scope1 = table.open_scope()

        error1 = symbol.SymbolError
        table.insert_symbol.when.called_with(expr).shouldnt.throw(error1)

        table.lookup_symbol(expr).should.be(expr)

        # Counter-intuitive, but this is what is needed.
        table.lookup_symbol(param).should.be(expr)

        table.lookup_symbol(ast.Param("bar")).should.be(None)

        with self.assertRaises(symbol.RedefIdentifierError) as context:
            table.insert_symbol(param)

        exc = context.exception
        exc.should.have.property("node").being(param)
        exc.should.have.property("prev").being(expr)

        scope2 = table.open_scope()
        table.insert_symbol.when.called_with(param).shouldnt.throw(error1)

        table.lookup_symbol(param).should.equal(param)
        table.lookup_symbol(expr).should.equal(param)

        scope3 = table.open_scope()
        table.lookup_symbol(expr, lookup_all=True).should.equal(param)
        scope2.visible = False
        table.lookup_symbol(param, lookup_all=True).should.equal(expr)

        table.close_scope()
        table.close_scope()
        table.close_scope()
