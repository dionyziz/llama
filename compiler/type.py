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

from collections import namedtuple

import compiler
from compiler import ast, error


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
            type(typecon()): self._validate_builtin
            for typecon in ast.builtin_types_map.values()
        }

        # Add dispatching for other types.
        self._dispatcher.update((
            (compiler.ast.Array, self._validate_array),
            (compiler.ast.Function, self._validate_function),
            (compiler.ast.Ref, self._validate_ref),
            (compiler.ast.User, self._validate_user)
        ))


    def validate(self, t):
        """Verify that a type is a valid type."""
        return self._dispatcher[type(t)](t)


class Table:
    """
    Database of all the program's types. Enables semantic checking
    of user defined types and more.
    """

    _TypeEntry = namedtuple('TypeEntry', ['key', 'list'])
    _ConstructorEntry = namedtuple('ConstructorEntry', ['key', 'type'])

    def __init__(self, logger):
        """Initialize a new Table."""
        self.logger = logger

        # Dictionary of types seen so far. Builtin types always available.
        #     Key:   Type node
        #     Value: A named 2-tuple (self, list), where
        #               key:  the Key
        #               list: list of Constructors which the type defines
        self.knownTypes = {}
        for t in ast.builtin_types_map.values():
            tt = t()
            self.knownTypes[tt] = self._TypeEntry(key=tt, list=None)

        # Dictionary of constructors encountered so far.
        #     Key:   Constructor node
        #     Value: A named 2-tuple (self, type), where
        #               key:  the Key
        #               type: Type which the constructor produces
        self.knownConstructors = {}

    # Logger used for logging events. Possibly shared with other modules.
    logger = None

    def process(self, typeDefList):
        """
        Analyse a user-defined type. Perform semantic checks
        and insert type in the TypeTable.
        """

        # First, insert all newly-defined types.
        for tdef in typeDefList:
            newType = tdef.type
            try:
                alias = self.knownTypes[newType].key
                if isinstance(alias, ast.Builtin):
                    self.logger.error(
                        "%d:%d: error: Redefining builtin type '%s'",
                        newType.lineno,
                        newType.lexpos,
                        newType.name
                    )
                else:
                    self.logger.error(
                        "%d:%d: error: Redefining user-defined type '%s'"
                        "\tPrevious definition: %d:%d",
                        newType.lineno,
                        newType.lexpos,
                        newType.name,
                        alias.lineno,
                        alias.lexpos
                    )
                return
            except KeyError:
                self.knownTypes[newType] = Table._TypeEntry(
                    key=newType,
                    list=[]
                )

        # Process each constructor.
        for tdef in typeDefList:
            newType = tdef.type
            for constructor in tdef:
                try:
                    alias = self.knownConstructors[constructor].key
                    self.logger.error(
                        "%d:%d: error: Redefining constructor '%s'"
                        "\tPrevious definition: %d:%d",
                        constructor.lineno,
                        constructor.lexpos,
                        constructor.name,
                        alias.lineno,
                        alias.lexpos
                    )
                    return
                except KeyError:
                    for argType in constructor:
                        if argType not in self.knownTypes:
                            self.logger.error(
                                "%d:%d: error: Undefined type '%s'",
                                argType.lineno,
                                argType.lexpos,
                                argType.name
                            )
                            return

                self.knownTypes[newType].list.append(constructor)
                self.knownConstructors[constructor] = Table._ConstructorEntry(
                    key=constructor,
                    type=newType
                )
        # TODO: Emit warnings when typenames clash with definition names.
