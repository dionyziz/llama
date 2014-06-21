"""
# ----------------------------------------------------------------------
# type.py
#
# Type management for Llama language
# http://courses.softlab.ntua.gr/compilers/2012a/llama2012.pdf
#
# Authors: Dionysis Zindros <dionyziz@gmail.com>
#          Dimitris Koutsoukos <dim.kou.shmmy@gmail.com>
#          Nick Korasidis <Renelvon@gmail.com>
# ----------------------------------------------------------------------
"""


class Type():
    name = None
    lineno = None
    lexpos = None

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


class Bool(Builtin):
    pass


class Float(Builtin):
    pass

builtin_map = {
    "bool": Bool,
    "char": Char,
    "float": Float,
    "int": Int,
    "unit": Unit,
}

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
        return all((
            isinstance(other, Array),
            self.dimensions == other.dimensions,
            self.type == other.type
        ))

    def __hash__(self):
        # Merkle-Damgard!
        return hash('array' + str(self.dimensions) + hash(self.type))


def String():
    """Factory method to alias (internally) String type to Array of char."""
    return Array(Char(), 1)


class Function(Type):
    def __init__(self, fromType, toType):
        self.fromType = fromType
        self.toType = toType

    def __eq__(self, other):
        return all((
            isinstance(other, Function),
            self.fromType == other.fromType,
            self.toType == other.toType
        ))

    def __hash__(self):
        # Merkle-Damgard!
        return hash('function' + hash(self.fromType) + hash(self.toType))


class Table(Type):
    """
    Database of all the program's types. Enables semantic checking
    of user defined types and more.
    """

    # Sets of types encountered so far. Built-in types always available.
    knownTypes = set(t() for t in builtin_map.values())

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
        for tdef in typeDefList:
            newtype = User(tdef.name)
            newtype.set_pos(tdef)
            if newtype in self.knownTypes:
                self._logger.error(
                    "%d:%d: error: Redefining type '%s'" % (
                        newtype.lineno,
                        newtype.lexpos,
                        newtype.name
                    )
                    # TODO Show previous definition
                )
            elif newtype.name in builtin_map:
                self._logger.error(
                    # FIXME Add meaningful line
                    "error: Cannot redefine builtin type: %s" % (newtype.name)
                    # TODO Show previous definition
                )
            else:
                self.knownTypes.add(newtype)

        # Process each constructor.
        for tdef in typeDefList:
            for constructor in tdef:
                if constructor.name in self.knownConstructors:
                    self._logger.error(
                        "%d:%d: error: Reusing constructor '%s'" % (
                            constructor.lineno,
                            constructor.lexpos,
                            constructor.name
                        )
                        # TODO Show previous use and type
                    )
                else:
                    for argType in constructor.list:
                        if argType not in self.knownTypes:
                            self._logger.error(
                                    "%d:%d: error: Undefined type '%s'" % (
                                    argType.lexpos,
                                    argType.lineno,
                                    argType.name
                                )
                            )
                    userType = User(tdef.name)
                    userType.set_pos(tdef)
                    self.knownConstructors[constructor.name] = {
                        "type": userType,
                        "params": constructor.list
                    }

        # TODO: Emmit warnings when typenames clash with definition names.
