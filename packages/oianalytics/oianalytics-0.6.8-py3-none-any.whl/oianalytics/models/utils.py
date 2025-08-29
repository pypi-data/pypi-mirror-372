import importlib.machinery


def reverse_dict(d: dict):
    return {v: k for k, v in d.items()}


def load_module_from_file(path: str):
    loader = importlib.machinery.SourceFileLoader("loaded_module", path)
    return loader.load_module("loaded_module")
