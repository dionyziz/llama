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
        node = ast.GenidExpression("foo")
        node.lineno, node.lexpos = 1, 2
        prev = ast.GenidExpression("foo")
        prev.lineno, prev.lexpos = 3, 4
        exc = symbol.RedefIdentifierError(node, prev)
        exc.should.be.a(symbol.SymbolError)
        exc.should.have.property("node").being(node)
        exc.should.have.property("prev").being(prev)

    @staticmethod
    def test_functionality():
        expr = ast.GenidExpression("foo")
        param = ast.Param("foo")

        table = symbol.SymbolTable()
        scope1 = table.open_scope()

        error1 = symbol.SymbolError
        table.insert_symbol.when.called_with(expr).shouldnt.throw(error1)

        table.lookup_symbol(expr).should.be(expr)

        # Counter-intuitive, but this is what is needed.
        table.lookup_symbol(param).should.be(expr)

        table.lookup_symbol(ast.Param("bar")).should.be(None)

        error2 = symbol.RedefIdentifierError
        table.insert_symbol.when.called_with(param).should.throw(error2)

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
