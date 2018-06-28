# rego-python

This repository contains a Python package for interacting with the [Open Policy Agent](https://github.com/open-policy-agent/opa) project's policy language: [Rego](https://www.openpolicyagent.org/docs/how-do-i-write-policies.html).

## Overview

module | description
--- | ---
`ast` | contains types representing Abstract Syntax Tree (AST) nodes in Rego.
`walk` | contains a visitor pattern implementation for `ast` types.

## Example: Load Rego AST from JSON

```python
import json
import requests

from rego import ast, walk

# Load some pi into OPA as data (yum!)
requests.put("http://localhost:8181/v1/data", data=json.dumps({
    "pi": 3.14,
}))

# Use OPA's Compile API to partially evaluate a query. Treat 'input.radius' as unknown.
resp = requests.post("http://localhost:8181/v1/compile", json.dumps({
    "query": "(data.pi * input.radius * 2) >= input.min_radius",
    "input": {
        "min_radius": 4,
    },
    "unknowns": ["input.radius"],
}))

# Load the resulting set of query ASTs out of the JSON response.
tree = resp.json()["result"]["queries"]
qs = ast.QuerySet.from_data(tree)

# Pretty print the ASTs.
walk.pretty_print(qs)
```

In a new terminal:

```
$ opa run --server
```

In another terminal, run the example.

```bash
$ git clone https://github.com/open-policy-agent/rego-python.git
$ cd rego-python
$ virtualenv env
$ source env/bin/activate
$ pip install -r example-requirements.txt
$ pip install -e .
$ python example.py
```

Example output.

```bash
QuerySet (1 queries)
  Query (1 exprs)
    Expr
      Term
        Ref
          Term
            Var(gte)
      Term
        Call
          Term
            Ref
              Term
                Var(mul)
          Term
            Call
              Term
                Ref
                  Term
                    Var(mul)
              Term
                Scalar(3.14)
              Term
                Ref
                  Term
                    Var(input)
                  Term
                    Scalar(radius)
          Term
            Scalar(2)
      Term
        Scalar(4)
```