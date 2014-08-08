import unittest

from compiler import error, symbol


class TestSymbolTableAPI(unittest.TestCase):
    """Test the API of the SymbolTable class."""

    @staticmethod
    def test_symboltable_init():
        symbol_table1 = symbol.SymbolTable()

        logger = error.LoggerMock()
        symbol_table2 = symbol.SymbolTable(logger=logger)

        symbol_table2.should.have.property("logger").being(logger)
