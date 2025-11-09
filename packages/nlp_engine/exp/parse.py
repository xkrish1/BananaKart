"""Inference utilities for BananaKart ingredient extraction."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch
from dateparser import parse as date_parse
from dateparser.search import search_dates
from transformers import (
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    AutoTokenizer,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NER_MODEL_DIR = PROJECT_ROOT / "model" / "token_classification"
CLS_MODEL_DIR = PROJECT_ROOT / "model" / "text_classification"

MAX_LEN_NER = 256
MAX_LEN_CLS = 128

QTY_RE = re.compile(
    r"(?P<num>(?:\d+[\d/\.\-]*|\d*\s*\d+\/\d+|[¼½¾⅓⅔⅛⅜⅝⅞]))\s*(?P<unit>[a-zA-Zµ]+\.?)?",
    re.IGNORECASE,
)

_QUANTITY_REGEX = re.compile(
    r"^(?P<num>(?:\d+\s+)?\d+(?:[\./]\d+)?|[¼½¾⅓⅔⅛⅜⅝⅞])\s*(?P<unit>[a-zA-Zµ%]+)?$"
)

_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_NER_RESOURCES: Dict[str, object] | None = None
_CLS_RESOURCES: Dict[str, object] | None = None

FRACTION_MAP = {
    "½": "1/2",
    "¼": "1/4",
    "¾": "3/4",
    "⅓": "1/3",
    "⅔": "2/3",
    "⅛": "1/8",
    "⅜": "3/8",
    "⅝": "5/8",
    "⅞": "7/8",
}

UNIT_NORMALIZATION = {
    "tbs": "tbsp",
    "tb": "tbsp",
    "tbl": "tbsp",
    "tbls": "tbsp",
    "teas": "tsp",
    "ts": "tsp",
}


@dataclass
class EntitySpan:
    label: str
    start: int
    end: int
    text: str


def _ensure_models_loaded() -> None:
    if not NER_MODEL_DIR.exists() or not CLS_MODEL_DIR.exists():
        raise FileNotFoundError(
            "Model checkpoints not found. Train models with "
            "`python train_token_classification.py` and "
            "`python train_text_classification.py` first."
        )

    global _NER_RESOURCES, _CLS_RESOURCES
    if _NER_RESOURCES is None:
        tokenizer = AutoTokenizer.from_pretrained(NER_MODEL_DIR)
        model = AutoModelForTokenClassification.from_pretrained(NER_MODEL_DIR)
        model.to(_DEVICE)
        model.eval()
        with (NER_MODEL_DIR / "label2id.json").open("r", encoding="utf-8") as f:
            label2id = {label: int(idx) for label, idx in json.load(f).items()}
        id2label = {idx: label for label, idx in label2id.items()}
        _NER_RESOURCES = {
            "tokenizer": tokenizer,
            "model": model,
            "label2id": label2id,
            "id2label": id2label,
        }

    if _CLS_RESOURCES is None:
        tokenizer = AutoTokenizer.from_pretrained(CLS_MODEL_DIR)
        model = AutoModelForSequenceClassification.from_pretrained(CLS_MODEL_DIR)
        model.to(_DEVICE)
        model.eval()
        with (CLS_MODEL_DIR / "label2id.json").open("r", encoding="utf-8") as f:
            label2id = {label: int(idx) for label, idx in json.load(f).items()}
        id2label = {idx: label for label, idx in label2id.items()}
        _CLS_RESOURCES = {
            "tokenizer": tokenizer,
            "model": model,
            "label2id": label2id,
            "id2label": id2label,
        }


def _token_classification(text: str) -> List[EntitySpan]:
    resources = _NER_RESOURCES
    assert resources is not None
    tokenizer = resources["tokenizer"]
    model = resources["model"]
    id2label = resources["id2label"]

    encoding = tokenizer(
        text,
        return_offsets_mapping=True,
        truncation=True,
        max_length=MAX_LEN_NER,
        return_tensors="pt",
    )
    offsets = encoding.pop("offset_mapping")[0].tolist()
    inputs = {k: v.to(_DEVICE) for k, v in encoding.items()}

    with torch.no_grad():
        logits = model(**inputs).logits
    predictions = torch.argmax(logits, dim=-1)[0].cpu().tolist()

    entities: List[EntitySpan] = []
    current_label: Optional[str] = None
    current_start: Optional[int] = None
    prev_end = 0

    for pred_id, (start, end) in zip(predictions, offsets):
        if start == end:
            continue  # special token
        label = id2label[int(pred_id)]
        if label == "O":
            if current_label is not None and current_start is not None:
                entities.append(
                    EntitySpan(
                        label=current_label,
                        start=current_start,
                        end=prev_end,
                        text=text[current_start:prev_end],
                    )
                )
                current_label = None
                current_start = None
        else:
            prefix, entity_type = label.split("-", 1)
            if prefix == "B" or current_label != entity_type:
                if current_label is not None and current_start is not None:
                    entities.append(
                        EntitySpan(
                            label=current_label,
                            start=current_start,
                            end=prev_end,
                            text=text[current_start:prev_end],
                        )
                    )
                current_label = entity_type
                current_start = start
        prev_end = end

    if current_label is not None and current_start is not None and prev_end >= current_start:
        entities.append(
            EntitySpan(
                label=current_label,
                start=current_start,
                end=prev_end,
                text=text[current_start:prev_end],
            )
        )

    return [ent for ent in entities if ent.text.strip()]


def _sequence_classification(text: str) -> str:
    resources = _CLS_RESOURCES
    assert resources is not None
    tokenizer = resources["tokenizer"]
    model = resources["model"]
    id2label = resources["id2label"]

    encoding = tokenizer(
        text,
        truncation=True,
        max_length=MAX_LEN_CLS,
        return_tensors="pt",
    )
    inputs = {k: v.to(_DEVICE) for k, v in encoding.items()}

    with torch.no_grad():
        logits = model(**inputs).logits
    prediction = int(torch.argmax(logits, dim=-1)[0].cpu().item())
    return id2label[prediction]


def _parse_number(text: str) -> Optional[float]:
    cleaned = text.strip()
    if not cleaned:
        return None
    for uni, ascii_frac in FRACTION_MAP.items():
        cleaned = cleaned.replace(uni, ascii_frac)
    cleaned = cleaned.replace("-", " ").replace("+", " ")
    try:
        return float(cleaned)
    except ValueError:
        pass
    if "/" in cleaned:
        try:
            numerator, denominator = cleaned.split("/", 1)
            return float(numerator) / float(denominator)
        except (ValueError, ZeroDivisionError):
            return None
    if " " in cleaned:
        parts = cleaned.split()
        if len(parts) == 2:
            try:
                whole = float(parts[0])
            except ValueError:
                whole = None
            frac = _parse_number(parts[1])
            if whole is not None and frac is not None:
                return whole + frac
    return None


def _parse_quantity(text: str) -> Tuple[Optional[float | str], Optional[str]]:
    candidate = text.strip()
    if not candidate:
        return None, None
    match = _QUANTITY_REGEX.match(candidate)
    if match:
        number_part = match.group("num")
        unit_part = match.group("unit")
        value = _parse_number(number_part)
        if value is not None:
            return value, unit_part.lower() if unit_part else None
    return candidate, None


def _normalize_entities(entities: List[EntitySpan]) -> List[Dict[str, Optional[object]]]:
    if not entities:
        return []
    entities = sorted(entities, key=lambda ent: ent.start)

    results: List[Dict[str, Optional[object]]] = []
    current: Dict[str, Optional[object]] | None = None
    pending: Dict[str, Optional[object]] = {"quantity": None, "unit": None, "form": None}

    def flush_current() -> None:
        nonlocal current
        if current is None:
            return
        normalized = {
            "name": current.get("name"),
            "quantity": current.get("quantity"),
            "unit": current.get("unit"),
            "form": current.get("form"),
        }
        if normalized["name"] is not None:
            results.append(normalized)
        current = None

    for ent in entities:
        value = ent.text.strip()
        if not value:
            continue
        if ent.label == "INGREDIENT":
            flush_current()
            quantity = pending["quantity"]
            unit = pending["unit"]
            form = pending["form"]
            pending = {"quantity": None, "unit": None, "form": None}
            current = {"name": value, "quantity": quantity, "unit": unit, "form": form}
        elif ent.label == "QTY":
            quantity_value, unit_hint = _parse_quantity(value)
            if current is not None and current.get("quantity") is None:
                current["quantity"] = quantity_value
                if unit_hint and not current.get("unit"):
                    current["unit"] = unit_hint
            else:
                pending["quantity"] = quantity_value
                if unit_hint and not pending.get("unit"):
                    pending["unit"] = unit_hint
        elif ent.label == "UNIT":
            if current is not None and current.get("unit") is None:
                unit_value = value.lower().rstrip(".")
                unit_value = UNIT_NORMALIZATION.get(unit_value, unit_value)
                current["unit"] = unit_value
            else:
                unit_value = value.lower().rstrip(".")
                unit_value = UNIT_NORMALIZATION.get(unit_value, unit_value)
                pending["unit"] = unit_value
        elif ent.label == "FORM":
            if current is not None and current.get("form") is None:
                current["form"] = value
            else:
                pending["form"] = value

    flush_current()
    return results


def _apply_fallback_quantities(
    text: str, ingredient_spans: List[Tuple[int, int]], ingredients: List[Dict[str, Optional[object]]]
) -> List[Dict[str, Optional[object]]]:
    if not ingredients or not ingredient_spans:
        return ingredients
    token_matches = list(re.finditer(r"\S+", text))
    if not token_matches:
        return ingredients

    for idx, item in enumerate(ingredients):
        if idx >= len(ingredient_spans):
            break
        if item.get("quantity") is not None and item.get("unit"):
            continue
        span_start, _ = ingredient_spans[idx]
        token_index = None
        for t_idx, token in enumerate(token_matches):
            if token.start() <= span_start < token.end():
                token_index = t_idx
                break
        if token_index is None:
            continue
        start_idx = max(0, token_index - 12)
        end_idx = min(len(token_matches), token_index + 13)
        window_start = token_matches[start_idx].start()
        window_end = token_matches[end_idx - 1].end()
        window_text = text[window_start:window_end]
        matches = list(QTY_RE.finditer(window_text))
        if not matches:
            continue
        best_match = min(matches, key=lambda m: abs((window_start + m.start()) - span_start))
        qty_val = _parse_number(best_match.group("num"))
        unit_val = best_match.group("unit")
        if qty_val is not None and (
            item.get("quantity") is None or (isinstance(item.get("quantity"), (int, float)) and abs(item["quantity"] - qty_val) > 1e-6)
        ):
            item["quantity"] = qty_val
        if unit_val:
            normalized_unit = unit_val.lower().rstrip(".")
            normalized_unit = UNIT_NORMALIZATION.get(normalized_unit, normalized_unit)
            if item.get("unit") in (None, "", normalized_unit):
                item["unit"] = normalized_unit
            elif item.get("unit") != normalized_unit:
                item["unit"] = normalized_unit
    return ingredients


def _infer_meal_time(urgency: str, tz: str, time_phrase: Optional[str] = None, text: Optional[str] = None) -> Optional[str]:
    settings = {
        "TIMEZONE": tz,
        "RETURN_AS_TIMEZONE_AWARE": True,
        "PREFER_DATES_FROM": "future",
    }
    phrase_source = time_phrase or text
    parsed = None
    if phrase_source:
        parsed = date_parse(phrase_source, settings=settings)
    if parsed is None and text:
        search_result = search_dates(text, settings=settings)
        if search_result:
            _, parsed = search_result[0]
    if parsed is not None:
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=datetime.now().astimezone().tzinfo)
        return parsed.astimezone().isoformat()

    now = datetime.now().astimezone()
    if urgency == "tonight":
        target = now.astimezone().replace(hour=18, minute=0, second=0, microsecond=0)
        if target < now:
            target += timedelta(days=1)
        return target.isoformat()
    if urgency == "this_week":
        future_date = (now + timedelta(days=7)).date()
        return future_date.isoformat()
    return None


def parse(text: str, tz: str = "America/New_York") -> Dict[str, object]:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("`text` must be a non-empty string")

    _ensure_models_loaded()

    entities = _token_classification(text)
    urgency = _sequence_classification(text)
    ingredients = _normalize_entities(entities)
    ingredient_spans = [(ent.start, ent.end) for ent in entities if ent.label == "INGREDIENT"]
    ingredients = _apply_fallback_quantities(text, ingredient_spans, ingredients)
    meal_time = _infer_meal_time(urgency=urgency, tz=tz, text=text)

    return {
        "ingredients": ingredients,
        "urgency": urgency,
        "meal_time": meal_time,
    }


if __name__ == "__main__":
    sample_text = "Need 2 tbsp olive oil and 200 g pasta for tonight at 7pm"
    result = parse(sample_text)
    from pprint import pprint

    pprint(result)
