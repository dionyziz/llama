import unittest

import sure

from compiler import parse, lex, error, ast, type


class TestParser(unittest.TestCase):
    def _parse(self, data, start='program'):
        mock = error.LoggerMock()

        lexer = lex.Lexer(logger=mock)
        parser = parse.Parser(
            logger=mock,
            optimize=0,
            start=start
        )

        tree = parser.parse(
            data=data,
            lexer=lexer
        )

        return tree

     def test_empty_program(self):
         self._parse("").should.be.equal(ast.Program([]))
 
     def test_empty_param_list(self):
         self._parse("", "param_list").should.be.equal([])
     
     def test_param_without_type(self):
         self._parse("my_parameter", "param").should.be.equal(ast.Param("my_parameter"))
 
     def test_param_with_type(self):
         self._parse("(my_parameter: int)", "param").should.be.equal(ast.Param("my_parameter", type.Int()))
