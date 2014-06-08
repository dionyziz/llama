import ast

class Type():
    def __init__(self):
        raise NotImplementedError

class Base(Type):
    def __init__(self):
        raise NotImplementedError

class Unit(Base):
    def __init__(self):
        pass

class Int(Base):
    def __init__(self):
        pass

class Char(Base):
    def __init__(self):
        pass

class Bool(Base):
    def __init__(self):
        pass

class Float(Base):
    def __init__(self):
        pass

class User(Type):
    def __init__(self, typename):
        self.typename = typename

class Ref(Type):
    def __init__(self, refType):
        self.refType = refType

class Array(Type):
    def __init__(self, type, dim=1):
        self.type = type
        self.dim = dim

class Function(Type):
    def __init__(self, fromType, toType):
        self.fromType = fromType
        self.toType = toType
