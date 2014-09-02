"""
# ----------------------------------------------------------------------
# symbol.py
#
# Symbol Table for the Llama language
# http://courses.softlab.ntua.gr/compilers/2012a/llama2012.pdf
#
# Authors: Nick Korasidis <Renelvon@gmail.com>
#          Dimitris Koutsoukos <dim.kou.shmmy@gmail.com>
# ----------------------------------------------------------------------
"""

from collections import defaultdict

from compiler import ast


class SymbolError(Exception):
    """
    Exception thrown on symbol table error.
    Carries the offending ast node(s).
    This class is only meant as an interface.
    Only specific sublcasses should be instantiated.
    """
    pass


class RedefIdentifierError(SymbolError):
    """Exception thrown on redefining identifier in same scope."""

    def __init__(self, node, prev):
        self.node = node
        self.prev = prev


class Scope:
    """
    A scope of the symbol table. Contains a list of entries,
    knows its nesting level and can be optionally hidden from lookup.
    """

    def __init__(self, entries, visible, nesting):
        """Make a new scope."""

        # List of names defined in the scope.
        # Mainly used for clean-up upon closing the scope.
        self.entries = entries

        # If the scope is not 'visible' then its entries should be hidden
        # from name lookup. In Llama, scopes are by default hidden upon
        # their creation. A name defined in a hidden scope cannot be used
        # until after the scope is made visible. This allows proper name
        # shadowing: the shadowed name's value can be correctly referenced
        # when initializing the shadowing names.
        # Exceptions: Some scopes are visible from the moment of their
        # creation, as for example those introduced by a 'let rec'.
        # This is necessary for implementing recursive definitions.
        self.visible = visible

        # Nesting level within the SymbolTable.
        # TODO: Should this be a read-only attribute?
        self.nesting = nesting


class SymbolTable:
    """A fully Pythonic symbol table for Llama."""

    class _Entry:
        """An entry of the symbol table."""
        # Reference to the ast node that the entry represents.
        # The node should contain the lineno and lexpos attributes.
        node = None

        # Reference to the symbol table scope containing the entry.
        # Used for fast lookup and sanity-checking.
        scope = None

        # Entry has an implicit identifier: node.name

        def __init__(self, node, scope):
            """Create a new symbol table entry from a NameNode."""
            self.node = node
            self.scope = scope

    _scopes = []
    nesting = 0       # Inv.: nesting == len(scopes)
    cur_scope = None  # Inv.: cur_scope == _scopes[-1] if _scopes else None

    # Each hashtable entry is a list containing symbols with
    # the same identifier, appearing at increasing scope depth.
    _hash_table = defaultdict(list)

    def __init__(self):
        """Make a new symbol table and insert the library namespace."""
        self._insert_library_symbols()

    def _insert_library_symbols(self):
        """Open a new scope populated with the library namespace."""
        # TODO: Dump library namespace here as a tuple of virtual AST nodes.
        lib_namespace = tuple()

        lib_scope = Scope(
            entries=[],
            visible=True,
            nesting=self.nesting
        )

        for node in lib_namespace:
            entry = self._Entry(node, lib_scope)
            lib_scope.entries.append(entry)

        self._push_scope(lib_scope)

    def _push_scope(self, scope):
        """Push 'scope' and maintain invariants."""
        self._scopes.append(scope)
        self.nesting += 1
        self.cur_scope = self._scopes[-1]

    def _pop_scope(self):
        """Pop scope and maintain invariants."""
        assert self._scopes, 'No scope to pop.'
        old_scope = self._scopes.pop()
        self.nesting -= 1
        if self._scopes:
            self.cur_scope = self._scopes[-1]
        else:
            self.cur_scope = None
        return old_scope

    def open_scope(self):
        """Open a new scope in the symbol table."""
        new_scope = Scope(
            entries=[],
            visible=True,
            nesting=self.nesting + 1
        )

        self._push_scope(new_scope)
        return new_scope

    def close_scope(self):
        """Close current scope in symbol table. Cleanup scope entries."""
        old_scope = self._pop_scope()
        for entry in old_scope.entries:
            ename = entry.node.name
            assert self._hash_table[ename], 'Identifier %s not found' % ename
            self._hash_table[ename].pop()
        return old_scope

#     def insert_scope(self, scope):
#         """Merge 'scope' with current scope."""
#         assert self.cur_scope, 'No scope to merge into.'
#         for entry in scope.entries:
#             entry.scope = self.cur_scope
#             self._hash_table[entry.node.name].append(entry)
#             self.cur_scope.entries.append(entry)
#

    def find_live_def(self, node):
        """
        Find the definition governing the given use of 'node',
        starting from the current scope and going upwards, honouring
        scope visibilities.
        If lookup succeeds, return the stored node, None otherwise.
        """
        ename = node.name
        for entry in reversed(self._hash_table[ename]):
            if entry.scope.visible:
                return entry.node
        return None

    def find_symbol_in_current_scope(self, node):
        """
        Lookup name of 'node' in current scope, ignoring visibility.
        If lookup succeeds, return the stored node, None otherwise.
        """
        assert self.cur_scope, 'No scope to search.'

        try:
            entry = self._hash_table[node.name][-1]
        except IndexError:
            # NOTE: Using defaultdict means KeyError never happens.
            return None

        enest = entry.scope.nesting
        if enest >= self.nesting:
            assert enest == self.nesting, "Entry nested deeper than it should."
            return entry.node
        return None

    def insert_symbol(self, node):
        """
        Insert a new NameNode in the current scope.
        Alert if an alias is already present in same scope.
        """
        assert self.cur_scope, 'No scope to insert into.'
        assert isinstance(node, ast.NameNode), 'Node is not a NameNode.'

        prev = self.find_symbol_in_current_scope(node)
        if prev is not None:
            raise RedefIdentifierError(node, prev)

        new_entry = self._Entry(node, self.cur_scope)
        self._hash_table[node.name].append(new_entry)
        self.cur_scope.entries.append(new_entry)
