import json
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
        if node.is_call():
            walk(node.operator, next)
            for o in node.operands:
                walk(o, next)
        else:
            walk(node.terms, next)
    elif isinstance(node, ast.Term):
        walk(node.value, next)
    elif isinstance(node, (ast.Ref, ast.Array, ast.Set, ast.Call)):
        for t in node.terms:
            walk(t, next)
    elif isinstance(node, ast.Object):
        for p in node.pairs:
            walk(p[0], next)
            walk(p[1], next)
    elif isinstance(node, ast.ObjectComprehension):
        walk(node.key, next)
        walk(node.value, next)
        walk(node.body, next)
    elif isinstance(node, (ast.SetComprehension, ast.ArrayComprehension)):
        walk(node.term, next)
        walk(node.body, next)


def pretty_print(node):
    class printer(object):
        def __init__(self, indent):
            self.indent = indent

        def __call__(self, node):
            if isinstance(node, ast.Scalar):
                name = node.__class__.__name__ + "(" + json.dumps(node.value) + ")"
            elif isinstance(node, ast.Var):
                name = node.__class__.__name__ + "(" + node.value + ")"
            else:
                name = node.__class__.__name__
            print(" " * self.indent + name)
            return printer(self.indent + 2)

    vis = printer(0)
    walk(node, vis)
