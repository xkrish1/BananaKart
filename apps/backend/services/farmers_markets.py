"""Utilities for looking up nearby farmers markets from a mock dataset."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "farmers_markets.json"

try:
    _MARKETS = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
except FileNotFoundError:
    _MARKETS = []


def find_markets(zipcode: str, limit: int = 3) -> List[dict]:
    """Return up to ``limit`` markets whose ZIP code matches the prefix."""
    if not zipcode:
        return []
    zipcode = zipcode.strip()
    matches = [
        market for market in _MARKETS if market.get("zipcode", "").startswith(zipcode)
    ]
    return matches[:limit]
