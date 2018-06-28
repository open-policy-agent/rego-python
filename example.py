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
