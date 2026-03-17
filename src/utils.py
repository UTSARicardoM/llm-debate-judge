#utils.py

import json
import os
from datetime import datetime


def ensure_directory(path: str) -> None:
    """
    Create a directory if it does not already exist.
    """

    os.makedirs(path, exist_ok=True)


def save_json(data: dict, path: str) -> None:
    """
    Save a Python dictionary to a JSON file.
    """

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def timestamp_string() -> str:
    """
    Return a compact timestamp string for filenames.
    """

    return datetime.now().strftime("%Y%m%d_%H%M%S")