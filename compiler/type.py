"""
# ----------------------------------------------------------------------
# type.py
#
# Semantic analysis of types
# http://courses.softlab.ntua.gr/compilers/2012a/llama2012.pdf
#
# Authors: Dionysis Zindros <dionyziz@gmail.com>
#          Dimitris Koutsoukos <dim.kou.shmmy@gmail.com>
#          Nick Korasidis <Renelvon@gmail.com>
# ----------------------------------------------------------------------
"""

from compiler import ast


class Table:
    """
    Database of all the program's types. Enables semantic checking
    of user defined types and more.
    """

    # Set of types encountered so far. Built-in types always available.
    knownTypes = set(t() for t in ast.builtin_map.values())

    # Dictionary of constructors encountered so far.
    # Each key contains a dict:
    #   type:    type which the constructor belongs to
    #   params:  type arguments of the constructor
    #   lineno:  line where constructor is defined
    #   lexpos:  column where constructor is defined
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
            newtype = ast.User(tdef.name)
            newtype.copy_pos(tdef)
            if newtype in self.knownTypes:
                self._logger.error(
                    "%d:%d: error: Redefining type '%s'" % (
                        newtype.lineno,
                        newtype.lexpos,
                        newtype.name
                    )
                    # TODO Show previous definition
                )
            elif newtype.name in ast.builtin_map:
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
                    alias = self.knownConstructors[constructor.name]
                    self._logger.error(
                        "%d:%d: error: Redefining constructor '%s'"
                        "\tPrevious definition: %d:%d" % (
                            constructor.lineno,
                            constructor.lexpos,
                            constructor.name,
                            alias['lineno'],
                            alias['lexpos']
                        )
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
                    userType = ast.User(tdef.name)
                    userType.copy_pos(tdef)
                    self.knownConstructors[constructor.name] = {
                        "type": userType,
                        "params": constructor.list,
                        "lineno": constructor.lineno,
                        "lexpos": constructor.lexpos
                    }

        # TODO: Emit warnings when typenames clash with definition names.
