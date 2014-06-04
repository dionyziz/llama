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
    pass

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
