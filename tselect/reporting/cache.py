import json
from pathlib import Path

CACHE_FILE = ".tselect_cache.json"


def load_cache(repo_root: Path):
    path = repo_root / CACHE_FILE
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def save_cache(repo_root: Path, data):
    path = repo_root / CACHE_FILE
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
