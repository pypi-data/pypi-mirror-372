import os
import json

dir_path = os.path.dirname(os.path.realpath(__file__))
conf_file = os.path.join(dir_path, "default.json")
with open(conf_file, "r") as f:
    config = json.load(f)


def get_config(key: str, default=None):
    return config.get(key, default)