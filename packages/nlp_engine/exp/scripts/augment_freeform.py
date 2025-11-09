import json
import os
import random
import re
from typing import Dict, List, Tuple

from rapidfuzz import fuzz, process

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "normalized")
OUT = os.path.join(DATA_DIR, "aug_freeform.jsonl")
random.seed(42)

TEMPLATES = [
    "I need {qty_unit} {name} for dinner.",
    "Grab {qty_unit} {name}.",
    "Please buy {qty_unit} {name} tonight.",
    "Pick up {qty_unit} {name} for the recipe.",
    "We’re cooking; get {qty_unit} {name}.",
    "Add {qty_unit} {name} to the cart.",
]


def qty_unit_str(quantity, unit):
    if quantity is None and not unit:
        return ""
    if quantity is None:
        return unit
    if isinstance(quantity, (int, float)) and float(quantity).is_integer():
        qtxt = str(int(quantity))
    else:
        qtxt = str(quantity)
    return f"{qtxt} {unit}".strip()


def spans_in_text(text: str, name: str, qtxt: str, utxt: str) -> List[Tuple[int, int, str]]:
    spans: List[Tuple[int, int, str]] = []
    if qtxt:
        idx = text.find(qtxt)
        if idx != -1:
            spans.append((idx, idx + len(qtxt), "QTY"))
    if utxt:
        idx = text.find(utxt)
        if idx != -1 and not (qtxt and text.find(qtxt) <= idx < text.find(qtxt) + len(qtxt)):
            spans.append((idx, idx + len(utxt), "UNIT"))
    if name:
        idx = text.lower().find(name.lower())
        if idx != -1:
            spans.append((idx, idx + len(name), "INGREDIENT"))
    return spans


def synth_from_struct(row: Dict) -> List[Dict]:
    out: List[Dict] = []
    for item in row.get("ingredients_struct") or []:
        name = (item.get("name") or "").strip()
        if not name:
            continue
        quantity = item.get("quantity")
        unit = (item.get("unit") or "").strip()
        qtxt = None
        if quantity is not None:
            if isinstance(quantity, (int, float)) and float(quantity).is_integer():
                qtxt = str(int(quantity))
            else:
                qtxt = str(quantity)
        utxt = unit or ""
        qty_unit = " ".join([x for x in [qtxt, utxt] if x]).strip()
        template = random.choice(TEMPLATES)
        sentence = template.format(qty_unit=qty_unit, name=name).replace("  ", " ").strip()
        spans = spans_in_text(sentence, name, qtxt or "", utxt)
        if spans:
            out.append({"text": sentence, "spans": spans, "source": "synth"})
    return out


def project_into_instructions(row: Dict, threshold: int = 90) -> List[Dict]:
    text = (row.get("text") or "")[:1000]
    if not text:
        return []
    out: List[Dict] = []
    for item in row.get("ingredients_struct") or []:
        name = (item.get("name") or "").strip()
        if not name:
            continue
        match = process.extractOne(name, [text], scorer=fuzz.token_set_ratio)
        if not match or match[1] < threshold:
            continue
        idx = text.lower().find(name.lower())
        if idx == -1:
            continue
        quantity = item.get("quantity")
        unit = (item.get("unit") or "").strip()
        window_left = max(0, idx - 30)
        window_right = min(len(text), idx + len(name) + 30)
        window = text[window_left:window_right]
        qty_match = re.search(r"(\d+\s*\d*/?\d*)", window)
        unit_match = re.search(r"\b[a-zA-Zµ]{1,6}\b", window)
        spans: List[Tuple[int, int, str]] = []
        spans.append((idx, idx + len(name), "INGREDIENT"))
        if qty_match:
            start = window_left + qty_match.start()
            end = window_left + qty_match.end()
            spans.append((start, end, "QTY"))
        if unit_match:
            start = window_left + unit_match.start()
            end = window_left + unit_match.end()
            spans.append((start, end, "UNIT"))
        if spans:
            out.append({
                "text": text[window_left:window_right],
                "spans": spans,
                "source": "projected",
            })
    return out


def main() -> None:
    rows: List[Dict] = []
    for filename in ["kaggle_food_recipes.jsonl", "recipe_nlg.jsonl"]:
        path = os.path.join(DATA_DIR, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                rows.extend(json.loads(line) for line in fh)
    augmented: List[Dict] = []
    for row in rows:
        augmented.extend(synth_from_struct(row))
        augmented.extend(project_into_instructions(row))
    with open(OUT, "w", encoding="utf-8") as fh:
        for example in augmented:
            fh.write(json.dumps(example, ensure_ascii=False) + "\n")
    print(f"Wrote {len(augmented)} records -> {OUT}")


if __name__ == "__main__":
    main()
