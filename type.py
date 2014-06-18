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
    """
    Database of all the program's types. Enables semantic checking
    of user defined types and more.
    """

    # Set of types encountered so far. Basic types always available.
    knownTypes = {'bool', 'int', 'float', 'char', 'unit'}

    # Dictionary of constructors encountered so far.
    # Each key contains a tuple (t, params), where:
    #   t is the type to which the constructor belongs
    #   params are the arguments of the constructor
    knownConstructors = {}

    # Logger used for logging events. Possibly shared with other modules.
    _logger = None

    def __init__(self, logger):
        """Return a new TypeTable."""
        self._logger = logger

    def process(self, typeDefList):
        """
        Analyse a user-defined type. Perform semantic checks
        and insert type in the TypeTable.
        """

        # First, insert all newly-defined types.
        for newtype in typeDefList:
            if newtype.name in self.knownTypes:
                self._logger.error(
                    #FIXME Add meaningful line
                    "error: Type reuse"
                    #TODO Show previous definition
                )
            else:
                self.knownTypes.add(newtype.name)

        # Process each constructor.
        for tdef in typeDefList:
            for c in tdef:
                if c.name in self.knownConstructors:
                    self._logger.error(
                        #FIXME add meaningful line
                        "error: Constructor reuse"
                        #TODO Show previous use
                    )
                else:
                    for t in c.list:
                        if t.name not in self.knownTypes:
                            self._logger.error(
                                #FIXME Add meaningful line
                                "error: Type not defined"
                            )
                    self.knownConstructors[c.name] = (tdef.name, c.list)
