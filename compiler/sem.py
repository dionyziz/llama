from compiler import ast
from compiler import type as tp


class TypeChecker:
    def map_datanode(self, node):
        print("Checking datanode of type " + type(node).__name__)
        print("Declared type is " + node.type.__class__.__name__)

        if node.type is None:
            return

        try:
            tp.validate(node.type)
        except tp.InvalidTypeError as e:
            print(('%d:%d: error: Invalid type: ' + {
                tp.ArrayOfArrayError: 'Array of array',
                tp.ArrayReturnError: 'Function returning array',
                tp.RefOfArrayError: 'Reference of array'
            }[type(e)]) % (e.node.lineno, e.node.lexpos))


def analyze(root):
    ast.map(root, obj=TypeChecker())
