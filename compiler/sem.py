from compiler import ast


class Walker:
    def walk_listnode(self, p):
        self.walk(p.list)

    def walk_list(self, l):
        for item in l:
            self.walk(item)

    def walk_program(self, p):
        self.walk_listnode(p)

    def walk_letdef(self, p):
        self.walk_listnode(p)

    def walk_functiondef(self, p):
        self.walk(p.params)
        self.walk(p.body)
        self.walk(p.type)

    def walk_param(self, p):
        self.walk(p.type)

    def walk_unaryexpression(self, p):
        self.walk(p.operand)

    def walk_binaryexpression(self, p):
        self.walk(p.leftOperand)
        self.walk(p.rightOperand)

    def walk_constructorcallexpression(self, p):
        self.walk_listnode(p)

    def walk_arrayexpression(self, p):
        self.walk_listnode(p)

    def walk_constexpression(self, p):
        self.walk(p.type)

    def walk_conidexpression(self, p):
        pass

    def walk_genidexpression(self, p):
        pass

    def walk_deleteexpression(self, p):
        self.walk(p.expr)

    def walk_dimexpression(self, p):
        pass

    def walk_forexpression(self, p):
        self.walk([
            p.counter,
            p.startExpr,
            p.stopExpr,
            p.body
        ])

    def walk_functioncallexpression(self, p):
        self.walk_list(p)

    def walk_letinexpression(self, p):
        self.walk(p.letdef)
        self.walk(p.expr)

    def walk_ifexpression(self, p):
        self.walk(p.condition)
        self.walk(p.thenExpr)
        self.walk(p.elseExpr)

    def walk_matchexpression(self, p):
        self.walk(p.expr)
        self.walk_listnode(p)

    def walk_clause(self, p):
        self.walk(p.pattern)
        self.walk(p.expr)

    def walk_pattern(self, p):
        self.walk_listnode(p)

    def walk_genidpattern(self, p):
        pass

    def walk_newexpression(self, p):
        self.walk(p.type)

    def walk_whileexpression(self, p):
        self.walk(p.condition)
        self.walk(p.body)

    def walk_arrayvariabledef(self, p):
        self.walk(p.dimensions)
        self.walk(p.type)

    def walk_variabledef(self, p):
        self.walk(p.type)

    def walk_typedeflist(self, p):
        # TODO: remove this once typedeflist is turned into a list
        self.walk_listnode(p)

    def walk_tdef(self, p):
        self.walk(p.type)
        self.walk_listnode(p)

    def walk_constructor(self, p):
        self.walk_listnode(p)

    def walk_nonetype(self, p):
        pass

    def walk_builtin(self, p):
        pass

    def walk_array(self, p):
        pass

    def walk_function(self, p):
        pass

    def walk_ref(self, p):
        pass

    def walk_user(self, p):
        pass

    def walk(self, p, f=None):
        if f is not None:
            f(p)
        if isinstance(p, ast.Builtin):
            self.walk_builtin(p)
        else:
            try:
                getattr(self, 'walk_' + type(p).__name__.lower())(p)
            except AttributeError:
                pass

def walk(root, f=None):
    Walker().walk(root, f)

def sem(root):
    Walker().walk(root)
