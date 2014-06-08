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
    def __init__(self, l):
        self.list = l

class TDef(Node):
    def __init__(self, name, l):
        self.name = name
        self.list = l

class Constr(Node):
    def __init__(self, name, l=None):
        self.name = name
        self.list = l if l is not None else []

class Param(DataNode):
    def __init__(self, name, type=None):
        self.name = name
        self.type = type

class LetDef(Node):
    def __init__(self, l):
        self.list = l

class LetRecDef(Node):
    def __init__(self, l):
        self.list = l

class Def(Node):
    def __init__():
        raise NotImplementedError

class FunctionDef(Def):
    def __init__(self, name, params, body, type=None):
        self.name = name
        self.params = params
        self.body = body
        self.type = type

class VariableDef(Def):
    def __init__(self, name, dataType=None):
        if isinstance(dataType, type.Array):
            raise TypeError
        self.name = name
        self.type = type

class ArrayVariableDef(VariableDef):
    def __init__(self, name, dimensions, dataType=None):
        self.name = name
        self.dimensions = dimensions
        self.dataType = dataType

class Expression(DataNode):
    pass

class BangExpression(Expression):
    def __init__(self, expr):
        self.expr = expr

class ArrayExpression(Expression):
    def __init__(self, name, l):
        self.name = name
        self.list = l

class IconstExpression(Expression):
    def __init__(self, value):
        self.value = value

class FconstExpression(Expression):
    def __init__(self, value):
        self.value = value

class CconstExpression(Expression):
    def __init__(self, value):
        self.value = value

class SconstExpression(Expression):
    def __init__(self, value):
        self.value = value

class BconstExpression(Expression):
    def __init__(self, value):
        self.value = value

class UconstExpression(Expression):
    def __init__(self):
        pass

class GenidExpression(Expression):
    def __init__(self, name):
        self.name = name

class ConidExpression(Expression):
    def __init__(self, name):
        self.name = name

class UnaryExpression(Expression):
    def __init__(self, operator, a):
        self.operator = operator
        self.a = a

class BinaryExpression(Expression):
    def __init__(self, a, operator, b):
        self.a = a
        self.operator = operator
        self.b = b

class GcallExpression(Expression):
    def __init__(self, name, params):
        self.name = name
        self.params = params

class CcallExpression(Expression):
    def __init__(self, name, params):
        self.name = name
        self.params = params

class DimExpression(Expression):
    def __init__(self, name, dimension=1):
        self.name = name
        self.dim = dimension

class NewExpression(Expression):
    def __init__(self, type):
        self.type = type

class DeleteExpression(Expression):
    def __init__(self, type):
        self.expr = expr

class IfExpression(Expression):
    def __init__(self, condition, thenExpr, elseExpr=None):
        self.condition = condition
        self.thenExpr = thenExpr
        self.elseExpr = elseExpr

class ForExpression(Expression):
    def __init__(self, counter, startExpr, stopExpr, body, downFlag=False):
        self.counter = counter
        self.startExpr = startExpr
        self.stopExpr = stopExpr
        self.body = body
        self.downFlag = downFlag

class WhileExpression(Expression):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class MatchExpression(Expression):
    def __init__(self, expr, l):
        self.expr = expr
        self.list = l

class LetInExpression(Expression):
    def __init__(self, definition, expr):
        self.definition = definition
        self.expr = expr

class Clause(Node):
    def __init__(self, pattern, expr):
        self.pattern = pattern
        self.expr = expr

class Pattern(Node):
    def __init__(self, name, l):
        self.name = name
        self.list = l

class IconstPattern(Node):
    def __init__(self, value):
        self.value = value

class FconstPattern(Node):
    def __init__(self, value):
        self.value = value

class CconstPattern(Node):
    def __init__(self, value):
        self.value = value

class SconstPattern(Node):
    def __init__(self, value):
        self.value = value

class BconstPattern(Node):
    def __init__(self, value):
        self.value = value

class GenidPattern(Node):
    def __init__(self, name):
        self.name = name
