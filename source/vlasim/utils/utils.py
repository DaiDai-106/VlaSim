import os
import json

def assets_path():
    """Return the project's `assets` directory. """
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root, "assets")

def load_json(json_file):
    if not os.path.exists(json_file):
        raise ValueError("Json file not found: {}".format(json_file))
    with open(json_file) as f:
        return json.load(f)
    return None