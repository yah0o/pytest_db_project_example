import json
from os import path


def load_schema(filename):
    filename = path.join(path.dirname(__file__), filename)
    with open(filename, 'r') as f:
        return json.load(f)


FAILED_RESPONSE = load_schema('failed_response.json')
