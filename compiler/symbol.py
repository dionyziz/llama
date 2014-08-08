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


    class _Scope:
        """
        A scope of the symbol table. Contains a list of entries,
        knows its nesting level and can be optionally hidden from lookup.
        """
        entries = []
        visible = True
        nesting = None

        def __init__(self, entries, visible, nesting):
            """Make a new scope."""
            self.entries = entries
            self.visible = visible
            self.nesting = nesting


    _scopes = []
    nesting = 0       # Inv.: nesting == len(scopes)
    cur_scope = None  # Inv.: cur_scope == _scopes[-1] if _scopes else None

    # Each hashtable entry is a list containing symbols with
    # the same identifier, appearing at increasing scope depth.
    hash_table = defaultdict(list)

    def __init__(self, logger):
        """Make a new symbol table and insert the library namespace."""
        self.logger = logger
        self._insert_library_symbols()

    def _insert_library_symbols(self):
        """Open a new scope populated with the library namespace."""
        # TODO: Dump library namespace here as a tuple of virtual AST nodes.
        lib_namespace = tuple()

        lib_scope = self._Scope(
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
        new_scope = self._Scope(
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
            assert self.hash_table[ename], 'Identifier %s not found' % ename
            self.hash_table[ename].pop()
        return old_scope

#     def insert_scope(self, scope):
#         """Merge 'scope' with current scope."""
#         assert self.cur_scope, 'No scope to merge into.'
#         for entry in scope.entries:
#             entry.scope = self.cur_scope
#             self.hash_table[entry.node.name].append(entry)
#             self.cur_scope.entries.append(entry)
#

    def lookup_symbol(self, node, lookup_all=False, guard=False):
        """
        Lookup name of 'node' in current scope.
        If 'lookup_all' is True, perform lookup in all scopes.
        If 'guard' is True, alert if name is absent from
        checked scope(s).
        If lookup succeeds, return the stored node, None otherwise.
        """

        ename = node.name
        if lookup_all:
            for entry in reversed(self.hash_table[ename]):
                if entry.scope.visible:
                    return entry.node
        else:
            entry = self._find_name_in_current_scope(ename)
            if entry is not None:
                return entry.node

        if guard:
            self.logger.error(
                "%d:%d: error: Unknown identifier: %s",
                node.lineno,
                node.lexpos,
                ename
            )
            # TODO: Raise an exception here.
        return None

    def _find_name_in_current_scope(self, name):
        """
        Lookup a name in the current scope.
        If lookup succeeds, return the entry, None otherwise.
        """
        assert self.cur_scope, 'No scope to search.'

        entry = self.hash_table[name][-1]

        if entry.scope.nesting != self.nesting:
            return None
        return entry

    def insert_symbol(self, node, guard=False):
        """
        Insert a new NameNode in the current scope.
        If 'guard' is True, alert if an alias is already present.
        """
        assert self.cur_scope, 'No scope to insert into.'
        assert isinstance(node, ast.NameNode), 'Node is not a NameNode.'

        new_name = node.name
        new_entry = self._Entry(node, self.cur_scope)

        if guard:
            entry = self._find_identifier_in_current_scope(new_name)
            if entry is not None:
                self.logger.error(
                    "%d:%d: error: Redefining identifier '%s' in same scope"
                    "\tPrevious definition: %d:%d",
                    node.lineno,
                    node.lexpos,
                    node.name,
                    entry.node.lineno,
                    entry.node.lexpos
                )
                # TODO: Raise some kind of exception here.

        self.hash_table[new_entry.identifier].append(new_entry)
        self.cur_scope.entries.append(new_entry)
