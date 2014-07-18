"""
# ----------------------------------------------------------------------
# ast.py
#
# AST constructors for the Llama language
# http://courses.softlab.ntua.gr/compilers/2012a/llama2012.pdf
#
# Authors: Dionysis Zindros <dionyziz@gmail.com>
#          Nick Korasidis <renelvon@gmail.com>
#
# ----------------------------------------------------------------------
"""

import inspect


# == INTERFACES OF AST NODES ==


class Node:
    lineno = None
    lexpos = None

    def __init__(self):
        raise NotImplementedError

    def __eq__(self, other):
        """
        Two nodes are equal if they are of the same type
        and have all attributes equal. Override as needed.
        """
        return type(self) == type(other) and all(
            getattr(self, attr) == getattr(other, attr)
            for attr in self.__dict__.keys()
            if attr not in ('lineno', 'lexpos')
        )

    def copy_pos(self, node):
        """Copy line info from another AST node."""
        self.lineno = node.lineno
        self.lexpos = node.lexpos

    def __repr__(self):
        attrs = [attr for attr in dir(self) if attr[0] != '_']
        values = [getattr(self, attr) for attr in attrs]
        safe_values = []
        for value in values:
            displayable_types = (int, float, bool, str, list, Type)
            if isinstance(value, displayable_types) or value is None:
                safe_values.append(str(value).replace("\n", "\n\t"))
            else:
                safe_values.append(
                    '(non-scalar of type %s)' % value.__class__.__name__
                )
        pairs = (
            "%s = '%s'" % (attr, value)
            for (attr, value) in zip(attrs, safe_values)
        )
        return "ASTNode:%s with attributes:\n\t* %s" \
               % (self.__class__.__name__, "\n\t* ".join(pairs))


class DataNode(Node):
    """A node to which a definite type can and should be assigned."""
    type = None


class Expression(DataNode):
    """An expression that can be evaluated."""
    pass


class Def(Node):
    """Definition of a new name."""
    pass


class NameNode(Node):
    """
    A node with a user-defined name.
    Provides basic hashing functionality.
    """
    name = None

    def __hash__(self):
        """Simple hash. Override as needed."""
        return hash(self.name)


class ListNode(Node):
    """
    A node carrying a list of ast nodes.
    Supports iterating through the nodes list.
    """
    list = None

    def __iter__(self):
        return iter(self.list)


class Type(Node):
    """A node representing a type."""
    pass


class Builtin(Type, NameNode):
    """One of the builtin types."""
    def __init__(self):
        self.name = self.__class__.__name__.lower()

# == AST REPRESENTATION OF PROGRAM ELEMENTS ==


class Program(ListNode):
    def __init__(self, list):
        self.list = list


class LetDef(ListNode):
    def __init__(self, list, isRec=False):
        self.list = list
        self.isRec = isRec


class FunctionDef(Def):
    def __init__(self, name, params, body, type=None):
        self.name = name
        self.params = params
        self.body = body
        self.type = type


class Param(DataNode):
    def __init__(self, name, type=None):
        self.name = name
        self.type = type


class BinaryExpression(Expression):
    def __init__(self, leftOperand, operator, rightOperand):
        self.leftOperand = leftOperand
        self.operator = operator
        self.rightOperand = rightOperand


class UnaryExpression(Expression):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand


class ConstructorCallExpression(Expression, ListNode):
    def __init__(self, name, list):
        self.name = name
        self.list = list


class ArrayExpression(Expression, ListNode):
    def __init__(self, name, list):
        self.name = name
        self.list = list


class ConstExpression(Expression):
    def __init__(self, type, value=None):
        self.type = type
        self.value = value


class ConidExpression(Expression):
    def __init__(self, name):
        self.name = name


class GenidExpression(Expression):
    def __init__(self, name):
        self.name = name


class DeleteExpression(Expression):
    def __init__(self, expr):
        self.expr = expr


class DimExpression(Expression):
    def __init__(self, name, dimension=1):
        self.name = name
        self.dimension = dimension


class ForExpression(Expression):
    def __init__(self, counter, startExpr, stopExpr, body, isDown=False):
        self.counter = counter
        self.startExpr = startExpr
        self.stopExpr = stopExpr
        self.body = body
        self.isDown = isDown


class FunctionCallExpression(Expression, ListNode):
    def __init__(self, name, list):
        self.name = name
        self.list = list


class LetInExpression(Expression):
    def __init__(self, letdef, expr):
        self.letdef = letdef
        self.expr = expr


class IfExpression(Expression):
    def __init__(self, condition, thenExpr, elseExpr=None):
        self.condition = condition
        self.thenExpr = thenExpr
        self.elseExpr = elseExpr


class MatchExpression(Expression, ListNode):
    def __init__(self, expr, list):
        self.expr = expr
        self.list = list


class Clause(Node):
    def __init__(self, pattern, expr):
        self.pattern = pattern
        self.expr = expr


class Pattern(ListNode):
    def __init__(self, name, list):
        self.name = name
        self.list = list


class GenidPattern(Node):
    def __init__(self, name):
        self.name = name


class NewExpression(Expression):
    def __init__(self, type):
        self.type = type


class WhileExpression(Expression):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


class VariableDef(Def):
    def __init__(self, name, type=None):
        self.name = name
        self.type = type


class ArrayVariableDef(VariableDef):
    def __init__(self, name, dimensions, type=None):
        self.name = name
        self.dimensions = dimensions
        self.type = type


class TypeDefList(ListNode):
    def __init__(self, list):
        self.list = list


class TDef(ListNode):
    def __init__(self, type, list):
        self.type = type
        self.list = list


class Constructor(NameNode, ListNode):
    def __init__(self, name, list=None):
        self.name = name
        self.list = list or []

# == REPRESENTATION OF TYPES AS AST NODES ==


class Bool(Builtin):
    pass


class Char(Builtin):
    pass


class Float(Builtin):
    pass


class Int(Builtin):
    pass


class Unit(Builtin):
    pass


builtin_types_map = {
    "bool": Bool,
    "char": Char,
    "float": Float,
    "int": Int,
    "unit": Unit,
}


class User(Type, NameNode):
    """A user-defined type."""

    def __init__(self, name):
        self.name = name


class Ref(Type):
    def __init__(self, type):
        self.type = type


class Array(Type):
    def __init__(self, type, dimensions=1):
        self.type = type
        self.dimensions = dimensions


def String():
    """Factory method to alias (internally) String type to Array of char."""
    return Array(Char(), 1)


class Function(Type):
    def __init__(self, fromType, toType):
        self.fromType = fromType
        self.toType = toType

def map(root, f=None):
    def map_listnode(p):
        map(p.list)

    def map_list(l):
        for item in l:
            map(item)

    def map_program(p):
        map_listnode(p)

    def map_letdef(p):
        map_listnode(p)

    def map_functiondef(p):
        map(p.params)
        map(p.body)
        map(p.type)

    def map_param(p):
        map(p.type)

    def map_unaryexpression(p):
        map(p.operand)

    def map_binaryexpression(p):
        map(p.leftOperand)
        map(p.rightOperand)

    def map_constructorcallexpression(p):
        map_listnode(p)

    def map_arrayexpression(p):
        map_listnode(p)

    def map_constexpression(p):
        map(p.type)

    def map_conidexpression(p):
        pass

    def map_genidexpression(p):
        pass

    def map_deleteexpression(p):
        map(p.expr)

    def map_dimexpression(p):
        pass

    def map_forexpression(p):
        map([
            p.counter,
            p.startExpr,
            p.stopExpr,
            p.body
        ])

    def map_functioncallexpression(p):
        map_list(p)

    def map_letinexpression(p):
        map(p.letdef)
        map(p.expr)

    def map_ifexpression(p):
        map(p.condition)
        map(p.thenExpr)
        map(p.elseExpr)

    def map_matchexpression(p):
        map(p.expr)
        map_listnode(p)

    def map_clause(p):
        map(p.pattern)
        map(p.expr)

    def map_pattern(p):
        map_listnode(p)

    def map_genidpattern(p):
        pass

    def map_newexpression(p):
        map(p.type)

    def map_whileexpression(p):
        map(p.condition)
        map(p.body)

    def map_arrayvariabledef(p):
        map(p.dimensions)
        map(p.type)

    def map_variabledef(p):
        map(p.type)

    def map_typedeflist(p):
        # TODO: remove this once typedeflist is turned into a list
        map_listnode(p)

    def map_tdef(p):
        map(p.type)
        map_listnode(p)

    def map_constructor(p):
        map_listnode(p)

    def map_nonetype(p):
        pass

    def map_builtin(p):
        pass

    def map_array(p):
        pass

    def map_function(p):
        pass

    def map_ref(p):
        pass

    def map_user(p):
        pass

    def map_node(p):
        if f is not None:
            f(p)
        if isinstance(p, ast.Builtin):
            map_builtin(p)
        else:
            for cls in inspect.getmro(p):
                try:
                    getattr('map_' + cls.__name__.lower())(p)
                except AttributeError:
                    pass

    map_node(root, f)
