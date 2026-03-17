#config_loader

import yaml


def load_config(path: str = "config.yaml") -> dict:
    """
    Load the YAML config file and return a dictionary.
    """

    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)