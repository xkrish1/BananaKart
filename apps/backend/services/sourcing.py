"""Helper utilities to allocate ingredients to farmers markets and big box stores."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

from apps.backend.services.farmers_markets import find_markets

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_BIG_BOX_PATH = _DATA_DIR / "big_box_stores.json"

try:
    _BIG_BOX_STORES = json.loads(_BIG_BOX_PATH.read_text(encoding="utf-8"))
except FileNotFoundError:
    _BIG_BOX_STORES = []


def _keyword_match(name: str, keywords: List[str]) -> bool:
    name_lower = name.lower()
    for keyword in keywords:
        if keyword and keyword.lower() in name_lower:
            return True
    return False


def allocate_ingredients(
    ingredients: List[Dict[str, object]],
    zipcode: str,
    market_limit: int = 5,
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
    """Return allocations (markets_alloc, big_box_alloc, unmatched_items)."""
    markets = find_markets(zipcode, limit=market_limit)
    remaining = list(ingredients)
    market_allocations: List[Dict[str, object]] = []

    for market in markets:
        matched = [
            item
            for item in remaining
            if isinstance(item, dict)
            and _keyword_match(str(item.get("name", "")), market.get("products", []))
        ]
        if matched:
            market_allocations.append({"market": market, "items": matched})
            remaining = [item for item in remaining if item not in matched]

    big_box_allocations: List[Dict[str, object]] = []
    stores = list(_BIG_BOX_STORES) or [
        {
            "name": "Generic BigBox",
            "address": "123 Retail Rd",
            "hours": "Daily 8:00-21:00",
            "inventory": ["pantry", "produce", "meat", "dairy"],
        }
    ]

    for store in stores:
        matched = [
            item
            for item in remaining
            if isinstance(item, dict)
            and _keyword_match(str(item.get("name", "")), store.get("inventory", []))
        ]
        if matched:
            big_box_allocations.append({"store": store, "items": matched})
            remaining = [item for item in remaining if item not in matched]

    if remaining:
        # Attach leftovers to first store for completeness
        big_box_allocations.append({"store": stores[0], "items": remaining})
        remaining = []

    return market_allocations, big_box_allocations, remaining
