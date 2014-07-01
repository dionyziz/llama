# ----------------------------------------------------------------------
# symbol.py
#
# Symbol Table for the Llama language
# http://courses.softlab.ntua.gr/compilers/2012a/llama2012.pdf
#
# Authors: Nick Korasidis <Renelvon@gmail.com>
#          Dimitris Koutsoukos <dim.kou.shmmy@gmail.com>
# ----------------------------------------------------------------------

from collections import defaultdict

import error as err


class Entry:
    """An entry of the symbol table. It knows which scope it's in."""
    identifier = None
    scope = None

    lexpos = None
    lineno = None

    def __init__(self, identifier, scope):
        self.identifier = identifier
        self.scope = scope
        # TODO: Initialize lineno and lexpos


class Scope:
    """
    A scope of the symbol table. Contains a list of entries,
    knows its nesting level and can be optionally hidden from lookup.
    """
    entries = []
    hidden = False
    nesting = None

    def __init__(self, entries, hidden, nesting):
        """Make a new scope."""
        self.entries = entries
        self.hidden = hidden
        self.nesting = nesting

    def hide_scope(self, hidden=True):
        """Hide visibility of scope."""
        self.hidden = hidden


class SymbolTable:
    """A fully Pythonic symbol table for Llama."""

    _scopes = []
    nesting = 0       # Inv.: nesting == len(scopes)
    cur_scope = None  # Inv.: cur_scope == _scopes[-1] if _scopes else None

    # Each hashtable entry is a list containing symbols with
    # the same identifier, appearing at increasing scope depth.
    hash_table = defaultdict(list)

    def __init__(self, logger):
        """Make a new symbol table and insert the library namespace."""
        self._logger = logger
        self._insert_library_symbols()

    def _insert_library_symbols(self):
        """Open a new scope populated with the library namespace."""
        lib_namespace = []  # TODO: Dump library namespace here

        lib_scope = Scope(
            entries=[],
            hidden=False,
            nesting=self.nesting
        )

        for identifier in lib_namespace:
            entry = Entry(identifier, lib_scope)
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
            hidden=False,
            nesting=self.nesting + 1
        )

        self._push_scope(new_scope)
        return new_scope

    def close_scope(self):
        """Close current scope in symbol table. Cleanup scope entries."""
        old_scope = self._pop_scope()
        for entry in old_scope.entries:
            eid = entry.identifier
            assert self.hash_table[eid], 'Identifier %s not found' % eid
            self.hash_table[entry.identifier].pop()
        return old_scope

#     def insert_scope(self, scope):
#         """Merge 'scope' with current scope."""
#         assert self.cur_scope, 'No scope to merge into.'
#         for entry in scope.entries:
#             entry.scope = self.cur_scope
#             self.hash_table[entry.identifier].append(entry)
#             self.cur_scope.entries.append(entry)
#

    def lookup_symbol(self, identifier, lookup_all=False, guard=False):
        """
        Lookup 'identifier' in current scope.
        If 'lookup_all' is True, perform lookup in all scopes.
        If 'guard' is True, alert if 'identifier' is absent from
        checked scope(s).
        """
        if lookup_all:
            for entry in reversed(self.hash_table[identifier]):
                if not entry.scope.hidden:
                    return entry
        else:
            entry = self._find_identifier_in_current_scope(identifier)
            if entry is not None:
                return entry

        if guard:
            self._logger.error(
                # FIXME: Meaningful line?
                "Unknown identifier: %s" % identifier
            )
        return None

    def _find_identifier_in_current_scope(self, identifier):
        assert self.cur_scope, 'No scope to check for identifier.'

        entry = self.hash_table[identifier][-1]

        if entry.scope.nesting != self.nesting:
            return None

        return entry

    def insert_symbol(self, identifier, guard=False):
        """
        Insert a new symbol in the current scope.
        If 'guard' is True, alert if an alias is already present.
        """
        assert self.cur_scope, 'No scope to insert into.'

        if guard:
            entry = self._find_identifier_in_current_scope(identifier)

            if entry is not None:
                self._logger.error(
                    # FIXME: Meaningful line?
                    "Duplicate identifier: %s" % identifier
                    # TODO: Show line of previous declaration
                )

                return entry

        new_entry = Entry(identifier=identifier, scope=self.cur_scope)
        self.hash_table[identifier].append(new_entry)
        self.cur_scope.entries.append(new_entry)

        return new_entry
