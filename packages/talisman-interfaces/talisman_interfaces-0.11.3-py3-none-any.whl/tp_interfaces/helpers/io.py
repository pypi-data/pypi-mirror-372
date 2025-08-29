import json
from pathlib import Path
from typing import Union


def check_path_existence(path: Path):
    if not path.exists():
        raise Exception(f"Path {path} does not exist")


def check_path_absense(path: Path):
    if path.exists():
        raise Exception(f"Path {path} already exists")


def check_or_create_empty_path(path: Path):
    if not path.exists():
        path.mkdir(parents=True)
    else:
        try:
            next(path.rglob("*"))
            raise Exception("Working path must not exist or must be empty")
        except StopIteration:
            pass


def read_json(path: Union[str, Path]):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
