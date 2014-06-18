# ----------------------------------------------------------------------
# type.py
#
# Type management for Llama language
# http://courses.softlab.ntua.gr/compilers/2012a/llama2012.pdf
#
# Authors: Dionysis Zindros <dionyziz@gmail.com>
#          Dimitris Koutsoukos <dimkou@gmail.com>
#          Nick Korasidis <Renelvon@gmail.com>
# ----------------------------------------------------------------------

class Type():
    def __init__(self):
        raise NotImplementedError

class Base(Type):
    def __init__(self):
        raise NotImplementedError

class Unit(Base):
    name = 'unit'
    def __init__(self):
        pass

class Int(Base):
    name = 'int'
    def __init__(self):
        pass

class Char(Base):
    name = 'char'
    def __init__(self):
        pass

class String(Char):
    name = 'string'
    def __init__(self):
        pass

class Bool(Base):
    name = 'bool'
    def __init__(self):
        pass

class Float(Base):
    name = 'float'
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

class TypeTable(Type):
    knownTypes = {'bool', 'int', 'float', 'char', 'unit'}
    knownConstructors = {}

    def __init__(self):
        pass

    def process(self, typeDefList):
        for newtype in typeDefList:
            if newtype.name in self.knownTypes:
                print("Type reuse")
            else:
                self.knownTypes.add(newtype.name)

        for tdef in typeDefList:
            for c in tdef:
                if c.name in self.knownConstructors:
                    print("Constructor reuse")
                else:
                    for t in c.list:
                        if t.name not in self.knownTypes:
                            print("Type not defined")
                    self.knownConstructors[c.name] = (tdef.name, c.list)
