import json
from pathlib import Path

MEMORY_FILE = Path(__file__).parent / "memory.json"


def load_memory() -> dict:
    if not MEMORY_FILE.exists():
        return {}

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_memory(memory: dict):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


def remember(key: str, value: str):
    memory = load_memory()
    memory[key] = value
    save_memory(memory)


def recall(key: str, default=None):
    memory = load_memory()
    return memory.get(key, default)


def forget(key: str):
    memory = load_memory()

    if key in memory:
        del memory[key]
        save_memory(memory)
        return True

    return False


def get_all_memory() -> dict:
    return load_memory()
