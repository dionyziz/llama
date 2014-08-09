import unittest

from compiler import ast, error, symbol


class TestSymbolTableAPI(unittest.TestCase):
    """Test the API of the SymbolTable class."""

    @staticmethod
    def test_symboltable_init():
        symbol_table1 = symbol.SymbolTable()

        logger = error.LoggerMock()
        symbol_table2 = symbol.SymbolTable(logger=logger)

        symbol_table2.should.have.property("logger").being(logger)

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
