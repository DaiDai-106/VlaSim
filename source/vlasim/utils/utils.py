import os

def assets_path():
    """Return the project's `assets` directory. """
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root, "assets")