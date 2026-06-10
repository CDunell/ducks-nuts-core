import json
import os
from pathlib import Path

_STORE = Path(os.getenv("SYMBOLS_PATH", "data/symbols.json"))

_DEFAULTS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "HYPEUSDT",
    "ADAUSDT", "SHIBUSDT", "AVAXUSDT", "LINKUSDT", "DOTUSDT",
]


def load() -> list:
    if _STORE.exists():
        return json.loads(_STORE.read_text())
    return [{"symbol": s, "enabled": True} for s in _DEFAULTS]


def save(data: list) -> None:
    _STORE.parent.mkdir(parents=True, exist_ok=True)
    _STORE.write_text(json.dumps(data, indent=2))


def active() -> list:
    return [e["symbol"] for e in load() if e["enabled"]]
