import json


def load_json(path):
    with open(path, 'rb') as file:
        data = json.load(file)
    return data
