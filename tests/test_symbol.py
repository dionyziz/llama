import unittest

from compiler import ast, symbol


class TestSymbolTableAPI(unittest.TestCase):
    """Test the API of the SymbolTable class."""

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
