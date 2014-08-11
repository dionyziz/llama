from compiler import ast, type


class TypeChecker:
    def map_datanode(self, node):
        try:
            type.validate(node.type)
        except InvalidTypeError as e:
            ('%d:%d: error: Invalid type: ' + {
                ArrayOfArrayError: 'Array of array',
                ArrayReturnError: 'Function returning array',
                RefOfArrayError: 'Reference of array'
            }[type(e)]) % (e.node.lineno, e.node.lexpos)


def analyze(root):
    ast.map(root, obj=TypeChecker())
