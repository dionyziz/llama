import ast

class Base():
    def __init__(self):
        raise NotImplementedError

class Unit(Base):
    pass

class Int(Base):
    pass

class Char(Base):
    pass

class Bool(Base):
    pass

class Float(Base):
    pass

class User(Base):
    def __init__(self, typename):
        self.typename = typename

class Ref(Base):
    def __init__(self, refType):
        self.refType = refType

class Array(Base):
    def __init__(self, refType, dim):
        self.refType = refType
        self.dim = dim

class Function(Base):
    def __init__(self, fromType, toType):
        self.fromType = fromType
        self.toType = toType
