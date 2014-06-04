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
    isRec = False

class TDef(Node):
    def __init__(self, l):
        self.list = l

class Constr(Node):
    def __init__(self, l):
        self.list = l

class Type(Node):
    def __init__(self):
        raise NotImplementedError

class UnitType(Type):
    pass

class IntType(Type):
    pass

class CharType(Type):
    pass

class BoolType(Type):
    pass

class FloatType(Type):
    pass

class UserType(Type):
    def __init__(self, typename):
        self.typename = typename

class RefType(Type):
    def __init__(self, refType):
        self.refType = refType

class ArrayType(Type):
    def __init__(self, refType, dim):
        self.refType = refType

class FunctionType(Type):
    def __init__(self, fromType, toType):
        self.fromType = fromType
        self.toType = toType

class Par(DataNode):
    pass

class Def(Node):
    pass

class GenId(DataNode):
    def __init__(self):
        pass

class Expression(DataNode):
    pass

class UnaryExpression(Expression):
    def __init__(self, operator, a):
        print("Unary expression (%s)" % (operator))
        self.operator = operator
        self.a = a

class BinaryExpression(Expression):
    def __init__(self, operator, a, b):
        print("Binary expression (%s)" % (operator))
        self.operator = operator
        self.a = a
        self.b = b
