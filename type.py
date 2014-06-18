# ----------------------------------------------------------------------
# type.py
#
# Type management for Llama language
# http://courses.softlab.ntua.gr/compilers/2012a/llama2012.pdf
#
# Author: Dionysis Zindros <dionyziz@gmail.com>
# ----------------------------------------------------------------------

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

class String(Char):
    def __init__(self):
        pass

class Bool(Base):
    def __init__(self):
        pass

class Float(Base):
    def __init__(self):
        pass

class User(Type):
    def __init__(self, name):
        self.name = name

class Ref(Type):
    def __init__(self, type):
        self.type = type

class Array(Type):
    def __init__(self, type, dim=1):
        self.type = type
        self.dim = dim

class Function(Type):
    def __init__(self, fromType, toType):
        self.fromType = fromType
        self.toType = toType
