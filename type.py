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
        if self.name is None or other.name is None:
            return False
        return self.name == other.name

    def __hash__(self):
        """Simple hash. Override as needed."""
        return hash(self.name)

class Builtin(Type):
    def __init__(self):
        self.name = self.__class__.__name__.lower()

class Unit(Builtin):
    pass

class Int(Builtin):
    pass

class Char(Builtin):
    pass

class String(Builtin):
    pass

class Bool(Builtin):
    pass

class Float(Builtin):
    pass

class User(Type):
    name = None

    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return hash('user' + self.name)

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

class Table(Type):
    """
    Database of all the program's types. Enables semantic checking
    of user defined types and more.
    """

    # Set of types encountered so far. Built-in types always available.
    knownTypes = {'bool', 'int', 'float', 'char', 'string', 'unit'}

    # Dictionary of constructors encountered so far.
    # Each key contains a dict:
    #   type:    type which the constructor belongs to
    #   params:  type arguments of the constructor
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
                    self.knownConstructors[constructor.name] = {
                        "type": tdef.name,
                        "params": constructor.list
                    }
