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
    name = None

    def __init__(self):
        raise NotImplementedError

    def __eq__(self, other):
        """Simple and strict type equality. Override as needed."""
        return self.name == other.name

    def __hash__(self):
        """Simple hash. Override as needed."""
        return hash(self.name)

class BaseType(Type):
    def __init__(self):
        raise NotImplementedError

class Unit(BaseType):
    name = 'unit'

    def __init__(self):
        pass

class Int(BaseType):
    name = 'int'

    def __init__(self):
        pass

class Char(BaseType):
    name = 'char'

    def __init__(self):
        pass

# NOTE: Why did this inherit from Char?
class String(BaseType):
    name = 'string'

    def __init__(self):
        pass

class Bool(BaseType):
    name = 'bool'

    def __init__(self):
        pass

class Float(BaseType):
    name = 'float'

    def __init__(self):
        pass

class User(Type):
    name = None

    def __init__(self, name):
        self.name = name

class Ref(Type):
    def __init__(self, type):
        self.type = type

    def __eq__(self, other):
        return isinstance(other, Ref) and self.type == other.type

    def __hash__(self):
        # Merkle-Damgard!
        return hash('ref' + hash(self.type))

class Array(Type):
    def __init__(self, type, dimensions=1):
        self.type = type
        self.dimensions = dimensions

    def __eq__(self, other):
        return isinstance(other, Array) and self.type == other.type and self.dimensions == other.dimensions

    def __hash__(self):
        # Merkle-Damgard!
        return hash('array' + str(self.dimensions) + hash(self.type))

class Function(Type):
    def __init__(self, fromType, toType):
        self.fromType = fromType
        self.toType = toType

    def __eq__(self, other):
        return isinstance(other, Function) and self.fromType == other.fromType and self.toType == other.toType

    def __hash__(self):
        # Merkle-Damgard!
        return hash('function' + hash(self.fromType) + hash(self.toType))

class TypeTable(Type):
    """
    Database of all the program's types. Enables semantic checking
    of user defined types and more.
    """

    # Set of types encountered so far. Basic types always available.
    knownTypes = {'bool', 'int', 'float', 'char', 'unit'}

    # Dictionary of constructors encountered so far.
    # Each key contains a tuple (t, params):
    #   t       type which the constructor belongs to
    #   params  type arguments of the constructor
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
                    # FIXME Add meaningful line
                    "error: Type reuse: %s" % (newtype.name)
                    # TODO Show previous definition
                )
            else:
                self.knownTypes.add(newtype.name)

        # Process each constructor.
        for tdef in typeDefList:
            for constructor in tdef:
                if constructor.name in self.knownConstructors:
                    self._logger.error(
                        # FIXME add meaningful line
                        "error: Constructor reuse: %s" % (constructor.name)
                        # TODO Show previous use
                    )
                else:
                    for argType in constructor.list:
                        if argType.name not in self.knownTypes:
                            self._logger.error(
                                # FIXME Add meaningful line
                                "error: Type not defined: %s" % (argType.name)
                            )
                    self.knownConstructors[constructor.name] = (
                        tdef.name,
                        constructor.list
                    )
