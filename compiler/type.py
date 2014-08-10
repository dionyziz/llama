"""
# ----------------------------------------------------------------------
# type.py
#
# Semantic analysis of types
# http://courses.softlab.ntua.gr/compilers/2012a/llama2012.pdf
#
# Authors: Nick Korasidis <renelvon@gmail.com>
#          Dimitris Koutsoukos <dim.kou.shmmy@gmail.com>
#          Dionysis Zindros <dionyziz@gmail.com>
# ----------------------------------------------------------------------
"""

from compiler import ast, smartdict


class InvalidTypeError(Exception):
    """Exception thrown on detecting an invalid type."""

    # The offending type node
    node = None

    def __init__(self):
        raise NotImplementedError


class ArrayOfArrayError(InvalidTypeError):
    """Exception thrown on detecting an array of arrays."""

    def __init__(self, node):
        self.node = node


class ArrayReturnError(InvalidTypeError):
    """Exception thrown on detecting a function returning an array."""

    def __init__(self, node):
        self.node = node


class RefofArrayError(InvalidTypeError):
    """Exception thrown on detecting a ref to an array."""

    def __init__(self, node):
        self.node = node


class Validator:
    """
    Type validator. Ensures type structure and semantics follow
    language spec.
    """

    _dispatcher = None

    @staticmethod
    def is_array(t):
        """Check if a type is an array type."""
        return isinstance(t, ast.Array)

    def _validate_array(self, t):
        """An 'array of T' type is valid iff T is a valid, non-array type."""
        basetype = t.type
        if self.is_array(basetype):
            raise ArrayOfArrayError(t)
        self.validate(basetype)

    @staticmethod
    def _validate_builtin(_):
        """A builtin type is always valid."""
        pass

    def _validate_function(self, t):
        """
        A 'T1 -> T2' type is valid iff T1 is a valid type and T2 is a
        valid, non-array type.
        """
        t1, t2 = t.fromType, t.toType
        if self.is_array(t2):
            raise ArrayReturnError(t)
        self.validate(t1)
        self.validate(t2)

    def _validate_ref(self, t):
        """A 'ref T' type is valid iff T is a valid, non-array type."""
        basetype = t.type
        if self.is_array(basetype):
            raise RefofArrayError(t)
        self.validate(basetype)

    @staticmethod
    def _validate_user(_):
        """A user-defined type is always valid."""
        pass

    def __init__(self):
        # FIXME: This should really become a closuere one day.
        """Create a new Validator."""

        # Bulk-add dispatching for builtin types.
        self._dispatcher = {
            typecon: self._validate_builtin
            for typecon in ast.builtin_types_map.values()
        }

        # Add dispatching for other types.
        self._dispatcher.update((
            (ast.Array, self._validate_array),
            (ast.Function, self._validate_function),
            (ast.Ref, self._validate_ref),
            (ast.User, self._validate_user)
        ))

    def validate(self, t):
        """Verify that a type is a valid type."""
        return self._dispatcher[type(t)](t)


class BadTypeDefError(Exception):
    """Exception thrown on detecting a bad type declaration."""

    def __init__(self):
        raise NotImplementedError


class RedefBuiltinTypeError(BadTypeDefError):
    """Exception thrown on detecting redefinition of builtin type."""

    def __init__(self, node):
        self.node = node


class RedefConstructorError(BadTypeDefError):
    """Exception thrown on detecting redefinition of constructor."""

    def __init__(self, node, prev):
        self.node = node
        self.prev = prev


class RedefUserTypeError(BadTypeDefError):
    """Exception thrown on detecting redefinition of user type."""

    def __init__(self, node, prev):
        self.node = node
        self.prev = prev


class UndefTypeError(BadTypeDefError):
    """Exception thrown on detecting reference to undefined type."""

    def __init__(self, node):
        self.node = node


class Table:
    """
    Database of all the program's types. Enables semantic checking
    of user defined types and more.
    """

    def __init__(self):
        """Initialize a new Table."""

        # Dictionary of types seen so far. Builtin types always available.
        # Values : list of constructors which the type defines
        # This is a smartdict, so keys can be retrieved.
        self.knownTypes = smartdict.Smartdict()
        for typecon in ast.builtin_types_map.values():
            self.knownTypes[typecon()] = None

        # Dictionary of constructors encountered so far.
        # Value: Type which the constructor produces.
        # This is a smartdict, so keys can be retrieved.
        self.knownConstructors = smartdict.Smartdict()

    def _insert_new_type(self, newType):
        """
        Insert newly defined type in Table. Signal error on redefinition.
        """
        existingType = self.knownTypes.getKey(newType)
        if existingType is None:
            self.knownTypes[newType] = []
            return

        if isinstance(existingType, ast.Builtin):
            raise RedefBuiltinTypeError(newType)
        else:
            raise RedefUserTypeError(newType, existingType)

    def _insert_new_constructor(self, newType, constructor):
        """Insert new constructor in Table. Signal error on reuse."""
        existingConstructor = self.knownConstructors.getKey(constructor)
        if existingConstructor is None:
            self.knownTypes[newType].append(constructor)
            self.knownConstructors[constructor] = newType

            for argType in constructor:
                if argType not in self.knownTypes:
                    raise UndefTypeError(argType)
        else:
            raise RedefConstructorError(constructor, existingConstructor)

    def process(self, typeDefList):
        """
        Analyse a user-defined type. Perform semantic checks
        and insert type in the TypeTable.
        """

        # First, insert all newly-defined types.
        for tdef in typeDefList:
            self._insert_new_type(tdef.type)

        # Then, process each constructor.
        for tdef in typeDefList:
            newType = tdef.type
            for constructor in tdef:
                self._insert_new_constructor(newType, constructor)

        # TODO: Emit warnings when typenames clash with definition names.
