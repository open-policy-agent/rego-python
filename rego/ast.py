import json


class QuerySet(object):
    def __init__(self, queries):
        self.queries = queries

    @classmethod
    def from_data(cls, data):
        return cls([Query.from_data(q) for q in data])

    def __str__(self):
        return self.__class__.__name__ + '(' + ', '.join(
            q.__class__.__name__ + '(' + str(q) + ')'
            for q in self.queries) + ')'


class Query(object):
    def __init__(self, exprs):
        self.exprs = exprs

    @classmethod
    def from_data(cls, data):
        return cls([Expr.from_data(e) for e in data])

    def __str__(self):
        return '; '.join(str(e) for e in self.exprs)


class Expr(object):
    def __init__(self, terms):
        self.terms = terms

    @property
    def operator(self):
        if not self.is_call():
            raise ValueError('not a call expr')
        return self.terms[0]

    @property
    def operands(self):
        if not self.is_call():
            raise ValueError('not a call expr')
        return self.terms[1:]

    def is_call(self):
        return not isinstance(self.terms, Term)

    def op(self):
        return ".".join(
            [str(t.value.value) for t in self.operator.value.terms])

    @classmethod
    def from_data(cls, data):
        terms = data["terms"]
        if isinstance(terms, dict):
            return cls(Term.from_data(terms))
        return cls([Term.from_data(t) for t in terms])

    def __str__(self):
        if self.is_call():
            return str(self.operator) + '(' + ', '.join(
                str(o) for o in self.operands) + ')'
        return str(self.terms)


class Term(object):
    def __init__(self, value):
        self.value = value

    @classmethod
    def from_data(cls, data):
        return cls(_VALUE_MAP[data["type"]].from_data(data["value"]))

    def __str__(self):
        return str(self.value)


class Scalar(object):
    def __init__(self, value):
        self.value = value

    @classmethod
    def from_data(cls, data):
        return cls(data)

    def __str__(self):
        return json.dumps(self.value)


class Var(object):
    def __init__(self, value):
        self.value = value

    @classmethod
    def from_data(cls, data):
        return cls(data)

    def __str__(self):
        return str(self.value)


class Ref(object):
    def __init__(self, terms):
        self.terms = terms

    def operand(self, idx):
        return self.terms[idx]

    @classmethod
    def from_data(cls, data):
        return cls([Term.from_data(x) for x in data])

    def __str__(self):
        return str(self.terms[0]) + ''.join('[' + str(t) + ']'
                                            for t in self.terms[1:])


class Array(object):
    def __init__(self, terms):
        self.terms = terms

    @classmethod
    def from_data(cls, data):
        return cls([Term.from_data(x) for x in data])

    def __str__(self):
        return '[' + ','.join(str(x) for x in self.terms) + ']'


class Set(object):
    def __init__(self, terms):
        self.terms = terms

    @classmethod
    def from_data(cls, data):
        return cls([Term.from_data(x) for x in data])

    def __str__(self):
        if len(self.terms) == 0:
            return 'set()'
        return '{' + ','.join(str(x) for x in self.terms) + '}'


class Object(object):
    def __init__(self, *pairs):
        self.pairs = pairs

    @classmethod
    def from_data(cls, data):
        return cls(
            *[(Term.from_data(p[0]), Term.from_data(p[1])) for p in data])

    def __str__(self):
        return '{' + ','.join({str(x): str(y) for (x, y) in self.pairs}) + '}'


class Call(object):
    def __init__(self, terms):
        self.terms = terms

    @classmethod
    def from_data(cls, data):
        return cls([Term.from_data(x) for x in data])

    @property
    def operator(self):
        return self.terms[0]

    @property
    def operands(self):
        return self.terms[1:]

    def op(self):
        return ".".join(
            [str(t.value.value) for t in self.operator.value.terms])

    def __str__(self):
        return str(self.operator) + '(' + ', '.join(
            str(o) for o in self.operands) + ')'


class ArrayComprehension(object):
    def __init__(self, term, body):
        self.term = term
        self.body = body

    @classmethod
    def from_data(cls, data):
        return cls(Term.from_data(data["term"]), Query.from_data(data["body"]))

    def __str__(self):
        return '[' + str(self.term) + ' | ' + str(self.body) + ']'


class SetComprehension(object):
    def __init__(self, term, body):
        self.term = term
        self.body = body

    @classmethod
    def from_data(cls, data):
        return cls(Term.from_data(data["term"]), Query.from_data(data["body"]))

    def __str__(self):
        return '{' + str(self.term) + ' | ' + str(self.body) + '}'


class ObjectComprehension(object):
    def __init__(self, key, value, body):
        self.key = key
        self.value = value
        self.body = body

    @classmethod
    def from_data(cls, data):
        return cls(
            Term.from_data(data["key"]), Term.from_data(data["value"]),
            Query.from_data(data["body"]))

    def __str__(self):
        return '{' + str(self.key) + ':' + str(self.value) + ' | ' + str(
            self.body) + '}'


def is_comprehension(x):
    """Returns true if this is a comprehension type."""
    return isinstance(
        x, (ObjectComprehension, SetComprehension, ArrayComprehension))


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
