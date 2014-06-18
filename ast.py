# ----------------------------------------------------------------------
# ast.py
#
# AST constructors for the Llama language
# http://courses.softlab.ntua.gr/compilers/2012a/llama2012.pdf
#
# Author: Dionysis Zindros <dionyziz@gmail.com>
#         Nick Korasidis <renelvon@gmail.com>
#
# ----------------------------------------------------------------------
import type

class Node:
    def __init__(self):
        raise NotImplementedError

class DataNode(Node):
    def __init__(self):
        raise NotImplementedError

class Program(DataNode):
    def __init__(self, list):
        self.list = list

class LetDef(Node):
    def __init__(self, list, isRec=False):
        self.list = list
        self.isRec = isRec

class Def(Node):
    def __init__(self):
        raise NotImplementedError

class FunctionDef(Def):
    def __init__(self, name, params, body, type=None):
        self.name = name
        self.params = params
        self.body = body
        self.type = type

class Param(DataNode):
    def __init__(self, name, type=None):
        self.name = name
        self.type = type

class Expression(DataNode):
    def __init__(self):
        raise NotImplementedError

class BinaryExpression(Expression):
    def __init__(self, leftOperand, operator, rightOperand):
        self.leftOperand = leftOperand
        self.operator = operator
        self.rightOperand = rightOperand

class UnaryExpression(Expression):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

class ConstructorCallExpression(Expression):
    def __init__(self, name, list):
        self.name = name
        self.list = list

class ArrayExpression(Expression):
    def __init__(self, name, list):
        self.name = name
        self.list = list

class ConstExpression(Expression):
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

class ConidExpression(Expression):
    def __init__(self, name):
        self.name = name

class GenidExpression(Expression):
    def __init__(self, name):
        self.name = name

class DeleteExpression(Expression):
    def __init__(self, expr):
        self.expr = expr

class DimExpression(Expression):
    def __init__(self, name, dimension=1):
        self.name = name
        self.dimension = dimension

class ForExpression(Expression):
    def __init__(self, counter, startExpr, stopExpr, body, isDown=False):
        self.counter = counter
        self.startExpr = startExpr
        self.stopExpr = stopExpr
        self.body = body
        self.isDown = isDown

class FunctionCallExpression(Expression):
    def __init__(self, name, list):
        self.name = name
        self.list = list

class LetInExpression(Expression):
    def __init__(self, letdef, expr):
        self.letdef = letdef
        self.expr = expr

class IfExpression(Expression):
    def __init__(self, condition, thenExpr, elseExpr=None):
        self.condition = condition
        self.thenExpr = thenExpr
        self.elseExpr = elseExpr

class MatchExpression(Expression):
    def __init__(self, expr, list):
        self.expr = expr
        self.list = list

class Clause(Node):
    def __init__(self, pattern, expr):
        self.pattern = pattern
        self.expr = expr

class Pattern(Node):
    def __init__(self, name, list):
        self.name = name
        self.list = list

class GenidPattern(Node):
    def __init__(self, name):
        self.name = name

class NewExpression(Expression):
    def __init__(self, type):
        self.type = type

class WhileExpression(Expression):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class VariableDef(Def):
    def __init__(self, name, type=None):
        self.name = name
        self.type = type

class ArrayVariableDef(VariableDef):
    def __init__(self, name, dimensions, itemType=None):
        self.name = name
        self.dimensions = dimensions
        self.type = type.Array(itemType, dimensions)

class TypeDefList(Node):
    def __init__(self, list):
        self.list = list

    def __iter__(self):
        return iter(self.list)

class TDef(Node):
    def __init__(self, name, list):
        self.name = name
        self.list = list

# FIXME Refactor me
    def __iter__(self):
        return iter(self.list)

class Constructor(Node):
    def __init__(self, name, list=None):
        self.name = name
        self.list = list or []

