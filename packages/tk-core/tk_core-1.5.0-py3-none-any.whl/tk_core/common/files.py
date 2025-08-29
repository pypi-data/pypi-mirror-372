import gzip
import pickle
from typing import Any

import ujson as json


def write_text(file_path: str, text: str) -> None:
    """Write text to .txt file locally"""
    with open(file_path, "w") as file:
        file.write(text)


def read_text(file_path: str) -> str:
    """Read text from .txt file locally"""
    with open(file_path) as file:
        return file.read()


def write_json(file_path: str, data: dict) -> None:
    """Write data to .json file locally"""
    with open(file_path, "w") as file:
        json.dump(data, file)


def read_json(file_path: str) -> dict:
    """Read data from .json file locally"""
    with open(file_path) as file:
        return json.load(file)


def safe_loads(s: str, default: Any = None) -> Any:
    """Safely load a string into a Python object, returning a default value if the load fails."""
    try:
        return json.loads(s)
    except Exception:
        return default


def pickle_write(file_name: str, data: Any) -> None:
    """
    takes a filename and data and writes it to pickle
    """
    with open(file_name, "wb") as fid:
        pickle.dump(data, fid, pickle.HIGHEST_PROTOCOL)


def pickle_read(file_name: str) -> Any:
    """
    takes a filename and reads from pickle
    """
    with open(file_name, "rb") as f:
        data = pickle.load(f)  # noqa: S301
    return data


def compress(s: str) -> bytes:
    # default to maximum compression (compresslevel=9)
    return gzip.compress(s.encode())
