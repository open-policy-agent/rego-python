class QuerySet(object):
    def __init__(self, *queries):
        self.queries = queries

    @classmethod
    def from_data(cls, data):
        return cls(*[Query.from_data(q) for q in data])

    def __str__(self):
        return '%s (%d queries)' % (self.__class__.__name__, len(self.queries),)


class Query(object):
    def __init__(self, *exprs):
        self.exprs = exprs

    @classmethod
    def from_data(cls, data):
        return cls(*[Expr.from_data(e) for e in data])

    def __str__(self):
        return '%s (%d exprs) ' % (self.__class__.__name__, len(self.exprs),)


class Expr(object):
    def __init__(self, operator, *operands):
        self.operator = operator
        self.operands = operands

    def op(self):
        return ".".join([str(t.value.value) for t in self.operator.value.terms])

    @classmethod
    def from_data(cls, data):
        terms = data["terms"]
        return cls(Term.from_data(terms[0]), *[Term.from_data(t) for t in terms[1:]])

    def __str__(self):
        return self.__class__.__name__


class Term(object):
    def __init__(self, value):
        self.value = value

    @classmethod
    def from_data(cls, data):
        return cls(_VALUE_MAP[data["type"]].from_data(data["value"]))

    def __str__(self):
        return self.__class__.__name__


class Scalar(object):
    def __init__(self, value):
        self.value = value

    @classmethod
    def from_data(cls, data):
        return cls(data)

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, str(self.value),)


class Var(object):
    def __init__(self, value):
        self.value = value

    @classmethod
    def from_data(cls, data):
        return cls(data)

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, self.value,)


class Ref(object):
    def __init__(self, *terms):
        self.terms = terms

    def operand(self, idx):
        return self.terms[idx]

    @classmethod
    def from_data(cls, data):
        return cls(*[Term.from_data(x) for x in data])

    def __str__(self):
        return self.__class__.__name__


class Array(object):
    def __init__(self, *terms):
        self.terms = terms

    @classmethod
    def from_data(cls, data):
        return cls(*[Term.from_data(x) for x in data])

    def __str__(self):
        return '%s (%d items) ' % (self.__class__.__name__, len(self.terms),)


class Set(object):
    def __init__(self, *terms):
        self.terms = terms

    @classmethod
    def from_data(cls, data):
        return cls(*[Term.from_data(x) for x in data])

    def __str__(self):
        return '%s (%d items) ' % (self.__class__.__name__, len(self.terms),)


class Object(object):
    def __init__(self, *pairs):
        self.pairs = pairs

    @classmethod
    def from_data(cls, data):
        return cls(*[(Term.from_data(p[0]), Term.from_data(p[1])) for p in data])

    def __str__(self):
        return '%s (%d items) ' % (self.__class__.__name__, len(self.pairs),)


class Call(object):
    def __init__(self, *terms):
        self.terms = terms

    @classmethod
    def from_data(cls, data):
        return cls(*[Term.from_data(x) for x in data])

    def __str__(self):
        return self.__class__.__name__


class ArrayComprehension(object):
    def __init__(self, term, body):
        self.term = term
        self.body = body

    @classmethod
    def from_data(cls, data):
        return cls(Term.from_data(data["term"]), Query.from_data(data["body"]))

    def __str__(self):
        return self.__class__.__name__


class SetComprehension(object):
    def __init__(self, term, body):
        self.term = term
        self.body = body

    @classmethod
    def from_data(cls, data):
        return cls(Term.from_data(data["term"]), Query.from_data(data["body"]))

    def __str__(self):
        return self.__class__.__name__


class ObjectComprehension(object):
    def __init__(self, key, value, body):
        self.key = key
        self.value = value
        self.body = body

    @classmethod
    def from_data(cls, data):
        return cls(Term.from_data(data["key"]), Term.from_data(data["value"]), Query.from_data(data["body"]))

    def __str__(self):
        return self.__class__.__name__


def is_comprehension(x):
    """Returns true if this is a comprehension type."""
    return isinstance(x, (ObjectComprehension, SetComprehension, ArrayComprehension))


_VALUE_MAP = {
    "null": Scalar,
    "boolean": Scalar,
    "number": Scalar,
    "string": Scalar,
    "var": Var,
    "ref": Ref,
    "array": Array,
    "set": Set,
    "object": Object,
    "call": Call,
    "objectcomprehension": ObjectComprehension,
    "setcomprehension": SetComprehension,
    "arraycomprehension": ArrayComprehension,
}
