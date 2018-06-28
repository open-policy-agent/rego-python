from rego import ast


def walk(node, vis):
    next = vis(node)
    if next is None:
        return

    if isinstance(node, ast.QuerySet):
        for q in node.queries:
            walk(q, next)
    elif isinstance(node, ast.Query):
        for e in node.exprs:
            walk(e, next)
    elif isinstance(node, ast.Expr):
        walk(node.operator, next)
        for o in node.operands:
            walk(o, next)
    elif isinstance(node, ast.Term):
        walk(node.value, next)
    elif isinstance(node, (ast.Ref, ast.Array, ast.Set, ast.Call)):
        for t in node.terms:
            walk(t, next)
    elif isinstance(node, ast.Object):
        for p in node.pairs:
            walk(p[0], next)
            walk(p[1], next)


def pretty_print(node):
    class printer(object):
        def __init__(self, indent):
            self.indent = indent

        def __call__(self, node):
            print ' ' * self.indent + str(node)
            return printer(self.indent+2)

    vis = printer(0)
    walk(node, vis)
