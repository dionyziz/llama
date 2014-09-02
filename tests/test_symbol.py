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

        # A couple of NameNodes
        expr = ast.GenidExpression("foo")
        expr.lineno, expr.lexpos = 1, 2
        param = ast.Param("foo")
        param.lineno, param.lexpos = 3, 4

        table = symbol.SymbolTable()

        # Open a scope and define "foo".
        table.open_scope()
        error1 = symbol.SymbolError
        table.insert_symbol.when.called_with(expr).shouldnt.throw(error1)

        # Query whether a "foo" is defined in current scope.
        table.find_symbol_in_current_scope(expr).should.be(expr)
        table.find_symbol_in_current_scope(param).should.be(expr)
        table.find_symbol_in_current_scope(ast.Param("bar")).should.be(None)

        # Find the live definition of a "foo"
        table.find_live_def(expr).should.be(expr)
        table.find_live_def(param).should.be(expr)
        table.find_live_def(ast.Param("bar")).should.be(None)

        # Check for scope effectiveness.
        table.open_scope()
        table.find_symbol_in_current_scope(expr).should.be(None)
        table.find_live_def(expr).should.be(expr)
        table.close_scope()

        # Reject inserting another "foo" in same scope
        with self.assertRaises(symbol.RedefIdentifierError) as context:
            table.insert_symbol(param)

        exc = context.exception
        exc.should.have.property("node").being(param)
        exc.should.have.property("prev").being(expr)

        # Open a new scope; define a new "foo"
        scope2b = table.open_scope()
        table.insert_symbol.when.called_with(param).shouldnt.throw(error1)

        # Query the newly defined "foo"
        table.find_symbol_in_current_scope(expr).should.be(param)
        table.find_symbol_in_current_scope(param).should.be(param)

        # Check for proper shadowing
        table.find_live_def(expr).should.be(param)
        table.find_live_def(param).should.be(param)

        # Check visibility honouring/ignoring.
        scope2b.visible = False
        table.find_live_def(param).should.be(expr)
        table.find_symbol_in_current_scope(param).should.be(param)
        scope2b.visible = True

        # Check for gracefull shutdown.
        table.close_scope()
        table.close_scope()
        table.close_scope()
