# ----------------------------------------------------------------------
# ast.py
#
# AST constructors for the Llama language
# http://courses.softlab.ntua.gr/compilers/2012a/llama2012.pdf
#
# Author: Dionysis Zindros <dionyziz@gmail.com>
#         Nick Korasidis <Renelvon@gmail.com>
#
# Lexer design is heavily inspired from the PHPLY lexer
# https://github.com/ramen/phply/blob/master/phply/phplex.py
# ----------------------------------------------------------------------

import type

class Node:
    def __init__(self):
        raise NotImplementedError

class DataNode(Node):
    def __init__(self):
        raise NotImplementedError

class Program(DataNode):
    def __init__(self, l):
        self.list = l

class TypeDef(Node):
    def __init__(self, typeSeq):
        self.typeSeq = typeSeq

class LetDef(Node):
    def __init__(self, l, isRec):
        self.list = l
        self.isRec = isRec

class TDef(Node):
    def __init__(self, l):
        self.list = l

class Constr(Node):
    def __init__(self, l):
        self.list = l

class Param(DataNode):
    def __init__(self, name, type):
        self.name = name
        self.type = type

class Def(Node):
    def __init__():
        raise NotImplementedError

class FunctionDef(Def):
    def __init__(self, name, params, body, type = None):
        self.name = name
        self.params = params
        self.body = body
        self.type = type

class VariableDef(Def):
    def __init__(self, name, dataType = None):
        if isinstance(dataType, type.Array):
            raise TypeError
        self.name = name
        self.type = type

class ArrayVariableDef(VariableDef):
    def __init__(self, name, dataType, arraySize):
        assert(isinstance(dataType, type.Array))

        self.name = name
        self.type = type
        self.arraySize = arraySize

class GenId(DataNode):
    def __init__(self):
        pass

class Expression(DataNode):
    pass

class UnaryExpression(Expression):
    def __init__(self, operator, a):
        # print("Unary expression (%s)" % (operator))
        self.operator = operator
        self.a = a

class BinaryExpression(Expression):
    def __init__(self, operator, a, b):
        # print("Binary expression (%s)" % (operator))
        self.operator = operator
        self.a = a
        self.b = b

class SimpleExpression(Expression):
    def __init__(self, value, type):
        self.value = value
        self.type = type

class ArrayExpression(Expression):
    def __init__(self, arrayId, indexSeq):
        self.arrayId = arrayId
        self.indexSeq = indexSeq

class BangExpression(Expression):
    def __init__(self, expr):
        self.expr = expr

class DimExpression(Expression):
    def __init__(self, arrayId, dimension):
        self.arrayId = arrayId
        self.dimension = dimension

class GenidExpression(Expression):
    def __init__(self, genid, params):
        self.genid = genid
        self.params = params

class ForDowntoExpression(Expression):
    def __init__(self, counter, startExpr, stopExpr, body):
        self.counter = counter
        self.startExpr = startExpr
        self.stopExpr = stopExpr
        self.body = body

class ForToExpression(Expression):
    def __init__(self, counter, startExpr, stopExpr, body):
        self.counter = counter
        self.startExpr = startExpr
        self.stopExpr = stopExpr
        self.body = body

class IfExpression(Expression):
    def __init__ (self, condition, thenExpr, elseExpr):
        self.condition = condition
        self.thenExpr = thenExpr
        self.elseExpr = elseExpr

class LetInExpression(Expression):
    def __init__(self, definition, expr):
        self.definition = definition
        self.expr = expr

class WhileExpression(Expression):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


