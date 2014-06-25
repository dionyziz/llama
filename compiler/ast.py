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


class Node:
    lineno = None
    lexpos = None

    def __init__(self):
        raise NotImplementedError

    def copy_pos(self, node):
        """Copy line info from another AST node."""
        self.lineno = node.lineno
        self.lexpos = node.lexpos

class ListNode(Node):
    list = None

    def __init__(self):
        raise NotImplementedError

    def __iter__(self):
        return iter(self.list)

class DataNode(Node):
    def __init__(self):
        raise NotImplementedError

class Program(DataNode):
    def __init__(self, list):
        self.list = list

class LetDef(Node):
    def __init__(self, list, isRec=False):
        self.list = list
        self.isRec = isRec

class Def(Node):
    def __init__(self):
        raise NotImplementedError

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

class Expression(DataNode):
    def __init__(self):
        raise NotImplementedError

class BinaryExpression(Expression):
    def __init__(self, leftOperand, operator, rightOperand):
        self.leftOperand = leftOperand
        self.operator = operator
        self.rightOperand = rightOperand

class UnaryExpression(Expression):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

class ConstructorCallExpression(Expression):
    def __init__(self, name, list):
        self.name = name
        self.list = list

class ArrayExpression(Expression):
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

class FunctionCallExpression(Expression):
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

class MatchExpression(Expression):
    def __init__(self, expr, list):
        self.expr = expr
        self.list = list

class Clause(Node):
    def __init__(self, pattern, expr):
        self.pattern = pattern
        self.expr = expr

class Pattern(Node):
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
    def __init__(self, name, dimensions, itemType=None):
        self.name = name
        self.dimensions = dimensions
        self.type = Array(itemType, dimensions)

class TypeDefList(ListNode):
    def __init__(self, list):
        self.list = list

class TDef(ListNode):
    def __init__(self, type, list):
        self.type = type
        self.list = list

class NameNode(Node):
    """An AST node with a name and basic equality testing."""
    name = None

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


class Constructor(NameNode, ListNode):
    def __init__(self, name, list=None):
        self.name = name
        self.list = list or []

# == AST REPRESENTATION OF TYPES ==

class Type(NameNode):
    """An AST node representing a type."""
    pass


class Builtin(Type):
    """One of llama's builtin types."""
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
    """A user-defined type."""

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
