"""
Utility script to clean a Food.com sample and emit sustainability labels.

Steps:
1. Load the Food.com sample stored in data/raw_foodcom_sample.json.
2. Standardize units, lowercase the text, and collapse whitespace.
3. Remove duplicate entries.
4. Attach lightweight sustainability labels inferred from key ingredients.
5. Persist the result to data/recipes_clean.json as a JSON list.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW_DATA = ROOT / "data" / "raw_foodcom_sample.json"
OUTPUT = ROOT / "data" / "recipes_clean.json"

UNIT_REPLACEMENTS: Dict[str, str] = {
    "lbs": "pounds",
    "lb": "pound",
    "oz": "ounces",
    "tsp": "teaspoon",
    "tbsp": "tablespoon",
    "c.": "cups",
    "c": "cups",
    "g": "grams",
    "kg": "kilograms",
    "ml": "milliliters",
}

INGREDIENT_PROFILES: Dict[str, Dict[str, float | bool]] = {
    "avocado": {"co2": 2.3, "local": False},
    "banana": {"co2": 0.9, "local": False},
    "tomato": {"co2": 0.8, "local": True},
    "kale": {"co2": 0.6, "local": True},
    "almond": {"co2": 2.8, "local": False},
    "chickpea": {"co2": 1.1, "local": True},
    "lentil": {"co2": 0.9, "local": True},
    "tofu": {"co2": 2.0, "local": True},
    "salmon": {"co2": 4.9, "local": False},
    "beef": {"co2": 27.0, "local": False},
    "chicken": {"co2": 6.9, "local": False},
    "oat": {"co2": 1.4, "local": True},
    "spinach": {"co2": 0.5, "local": True},
    "carrot": {"co2": 0.3, "local": True},
    "potato": {"co2": 0.4, "local": True},
    "mushroom": {"co2": 1.0, "local": True},
    "broccoli": {"co2": 0.6, "local": True},
    "zucchini": {"co2": 0.4, "local": True},
    "sweet potato": {"co2": 0.4, "local": True},
    "apple": {"co2": 0.5, "local": True},
    "berry": {"co2": 0.8, "local": True},
    "peanut": {"co2": 2.4, "local": False},
    "cauliflower": {"co2": 0.5, "local": True},
    "black bean": {"co2": 1.0, "local": True},
    "cabbage": {"co2": 0.2, "local": True},
    "pea": {"co2": 0.3, "local": True},
    "beet": {"co2": 0.3, "local": True},
    "mango": {"co2": 1.5, "local": False},
    "pineapple": {"co2": 1.6, "local": False},
    "turkey": {"co2": 10.9, "local": False},
    "tempeh": {"co2": 1.8, "local": True},
    "quinoa": {"co2": 1.5, "local": False},
    "farro": {"co2": 1.4, "local": True},
}

FALLBACK_LABEL = {"ingredient": "mixed produce", "local": True, "co2": 1.5}


def standardize_units(text: str) -> str:
    lowered = text.lower()
    for short, full in UNIT_REPLACEMENTS.items():
        lowered = re.sub(rf"\b{re.escape(short)}\b", full, lowered)
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return lowered


def flatten_ingredients(value: str | List[str]) -> str:
    if isinstance(value, list):
        return ", ".join(value)
    return str(value)


def infer_label(text: str) -> Dict[str, float | bool | str]:
    for ingredient, meta in INGREDIENT_PROFILES.items():
        if ingredient in text:
            return {"ingredient": ingredient, "local": bool(meta["local"]), "co2": round(float(meta["co2"]), 2)}
    return FALLBACK_LABEL


def build_dataset(limit: int = 500) -> List[Dict[str, object]]:
    df = pd.read_json(RAW_DATA)
    df["ingredients_text"] = df["ingredients"].apply(flatten_ingredients)
    df["clean_ingredients"] = df["ingredients_text"].apply(standardize_units)
    df["clean_title"] = df["title"].apply(lambda t: standardize_units(str(t)))
    df["clean_description"] = df["description"].fillna("").apply(standardize_units)
    df["input"] = (
        df["clean_title"]
        + " | ingredients: "
        + df["clean_ingredients"]
        + " | description: "
        + df["clean_description"]
    )
    df = df.drop_duplicates(subset=["input"]).head(limit)
    df["label"] = df["clean_ingredients"].apply(infer_label)
    return df[["input", "label"]].to_dict("records")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    records = build_dataset()
    with OUTPUT.open("w", encoding="utf-8") as fp:
        json.dump(records, fp, indent=2)
    print(f"Wrote {len(records)} cleaned samples to {OUTPUT}")


if __name__ == "__main__":
    main()
