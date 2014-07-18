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

from compiler import ast, error, smartdict


class LlamaInvalidTypeError(Exception):
    """Exception thrown on detecting an invalid type."""
    pass


class LlamaBadTypeError(Exception):
    """Exception thrown on detecting a bad type declaration."""
    pass


class Validator:
    """
    Type validator. Ensures type structure and semantics follow
    language spec.
    """

    # Logger used for logging events. Possibly shared with other modules.
    logger = None
    _dispatcher = None

    @staticmethod
    def is_array(t):
        """Check if a type is an array type."""
        return isinstance(t, ast.Array)

    def _validate_array(self, t):
        """An 'array of T' type is valid iff T is a valid, non-array type."""
        basetype = t.type
        if self.is_array(basetype):
            self.logger.error(
                "%d:%d: error: Invalid type: Array of array",
                t.lineno,
                t.lexpos
            )
            return False
        return self.validate(basetype)

    def _validate_builtin(self, t):
        """A builtin type is always valid."""
        return True

    def _validate_function(self, t):
        """
        A 'T1 -> T2' type is valid iff T1 is a valid type and T2 is a
        valid, non-array type.
        """
        t1, t2 = t.fromType, t.toType
        if self.is_array(t2):
            self.logger.error(
                "%d:%d: error: Invalid type: Function returning array",
                t.lineno,
                t.lexpos
            )
            return False
        return self.validate(t1) and self.validate(t2)

    def _validate_ref(self, t):
        """A 'ref T' type is valid iff T is a valid, non-array type."""
        basetype = t.type
        if self.is_array(basetype):
            self.logger.error(
                "%d:%d: error: Invalid type: Reference of array",
                t.lineno,
                t.lexpos
            )
            return False
        return self.validate(basetype)

    def _validate_user(self, t):
        """A user-defined type is always valid."""
        return True

    def __init__(self, logger=None):
        """Create a new Validator."""
        if logger is None:
            self.logger = error.Logger(inputfile='<stdin>')
        else:
            self.logger = logger

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


class Table:
    """
    Database of all the program's types. Enables semantic checking
    of user defined types and more.
    """

    # Logger used for logging events. Possibly shared with other modules.
    logger = None

    def __init__(self, logger):
        """Initialize a new Table."""
        self.logger = logger

        # Dictionary of types seen so far. Builtin types always available.
        # Values : list of constructors which the type defines
        # This is a smartdict, so keys can be retrieved.
        self.knownTypes = smartdict.Smartdict()
        for t in ast.builtin_types_map.values():
            self.knownTypes[t()] = None

        # Dictionary of constructors encountered so far.
        # Value: Type which the constructor produces.
        # This is a smartdict, so keys can be retrieved.
        self.knownConstructors = smartdict.Smartdict()

    def _signal_error(self, msg, *args):
        self.logger.error(msg, *args)
        raise LlamaBadTypeError  # Notify semantic analyzer.

    def _insert_new_type(self, newType):
        existingType = self.knownTypes.getKey(newType)
        if existingType is None:
            self.knownTypes[newType] = []
            return

        if isinstance(existingType, ast.Builtin):
            self._signal_error(
                "%d:%d: error: Redefining builtin type '%s'",
                newType.lineno,
                newType.lexpos,
                newType.name
            )
        else:
            self._signal_error(
                "%d:%d: error: Redefining user-defined type '%s'"
                "\tPrevious definition: %d:%d",
                newType.lineno,
                newType.lexpos,
                newType.name,
                existingType.lineno,
                existingType.lexpos
            )

    def _insert_new_constructor(self, newType, constructor):
        existingConstructor = self.knownConstructors.getKey(constructor)
        if existingConstructor is None:
            self.knownTypes[newType].append(constructor)
            self.knownConstructors[constructor] = newType

            for argType in constructor:
                if argType not in self.knownTypes:
                    self._signal_error(
                        "%d:%d: error: Undefined type '%s'",
                        argType.lineno,
                        argType.lexpos,
                        argType.name
                    )
        else:
            self._signal_error(
                "%d:%d: error: Redefining constructor '%s'"
                "\tPrevious definition: %d:%d",
                constructor.lineno,
                constructor.lexpos,
                constructor.name,
                existingConstructor.lineno,
                existingConstructor.lexpos
            )

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
