# ----------------------------------------------------------------------
# symbol.py
#
# Symbol Table for the Llama language
# http://courses.softlab.ntua.gr/compilers/2012a/llama2012.pdf
#
# Author: Nick Korasidis <Renelvon@gmail.com>
#       : Dimitris Koutsoukos <dimkou.shmmy@gmail.com>
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


class Scope:
    """
    A scope of the symbol table. Contains a set of entries,
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
        return self

    def hide_scope(self, hidden):
        """Hide visibility of scope."""
        self.hidden = hidden


class SymbolTable:
    """A fully Pythonic symbol table for Llama."""

    _scopes = []
    nesting = 0       # Inv.: nesting == len(scopes)
    cur_scope = None  # Inv.: cur_scope == _scopes[-1] if _scopes else None

    """
    Each hashtable entry is a list containing symbols with
    the same identifier, appearing at increasing scope depth. The last
    element is the symbol appearing in the current scope.
    """
    hash_table = defaultdict(list)

    def __init__(self):
        """
        Make a new symbol table. The table already
        contains a scope populated with the library namespace.
        """
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
        return self

    def _push_scope(self, scope):
        """Push scope and maintain nesting invariant."""
        self._scopes.append(scope)
        self.nesting += 1
        self.curScope = self._scopes[-1]

    def _pop_scope(self):
        """Pop scope and maintain nesting invariant."""
        assert self.scopes, 'No scope to pop.'
        self.nesting -= 1
        old_scope = self._scopes.pop()
        if self._scopes:
            self.cur_scope = _scopes[-1]
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
            eid = entry,identifier
            assert eid in self.hash_table, 'Identifier %s not found' % eid
            self.hash_table[entry.identifier].pop()
        return old_scope

    def insert_scope(self, scope):
        """Merge scope with current scope."""
        assert self.cur_scope, 'No scope to merge into.'
        for entry in scope.entries:
            assert self.cur_scope, 'Merging into null scope.'
            entry.scope = self.cur_scope
            self.hash_table[entry.identifier].append(entry)
            self.cur_scope.entries.append(entry)

    def lookup_symbol(identifier, lookup_all, guard=False):
        """
        Lookup 'identifier' in current scope.
        If 'lookup_all' is True, perform lookup in all scopes.
        If 'guard' is True, alert if 'identifier' is not present
        in checked scope(s).
        """
        if lookup_all:
            for entry in reversed(self.hash_table[identifier]):
                if not entry.scope.hidden:
                    return entry
        else:
            for entry in reversed(self.hash_table[identifier]):
                if not entry.scope.hidden:
                    if entry.scope.nesting < self.nesting:
                        break
                    return entry

        if guard:
            err.push_error(
                0,  # FIXME: Meaningful line?
                "Unknown identifier: %s" % identifier
            )
        return None

    def insert_symbol(self, identifier, guard=False):
        """
        Insert a new symbol in the current scope.
        If 'guard' is True, alert if an alias is already present.
        """
        assert self.cur_scope, 'No scope to insert into.'
        if guard:
            for entry in reversed(self.hash_table[identifier]):
                if entry.scope.nesting < self.nesting:
                    break

                if entry.identifier == identifier:
                    err.push_error(
                        0,  # FIXME: Meaningful line?
                        "Duplicate identifier: %s" % identifier
                        # TODO: Show line of previous declaration
                    )
                    return None

        new_entry = Entry(identifier=identifier, scope=self.cur_scope)
        self.hash_table[identifier].append(new_entry)
        self.cur_scope.entries.append(new_entry)

        return new_entry