import os, json, re
from typing import List, Dict, Tuple
from datasets import Dataset, Features, Value, Sequence
from transformers import AutoTokenizer
from scripts.common import BASE_MODEL, save_json, set_seed

DATA_IN = os.path.join(os.path.dirname(__file__), "..", "data", "normalized")
AUG_PATH = os.path.join(DATA_IN, "aug_freeform.jsonl")
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "cache")
META_DIR = os.path.join(CACHE_DIR, "meta")
os.makedirs(CACHE_DIR, exist_ok=True); os.makedirs(META_DIR, exist_ok=True)

NER_TAGS = ["O","B-INGREDIENT","I-INGREDIENT","B-QTY","I-QTY","B-UNIT","I-UNIT"]
CLS_LABELS = {"tonight":0,"this_week":1,"flexible":2}

BULLET = "• "


def build_ingredient_lines(ings: List[Dict]) -> Tuple[str, List[Tuple[int,int,str]]]:
    """
    Returns:
      text: multi-line ingredient list
      spans: list of (start, end, label) for QTY, UNIT, INGREDIENT
    """
    lines = []
    spans = []
    cursor = 0
    for item in ings:
        name = (item.get("name") or "").strip()
        q = item.get("quantity")
        u = (item.get("unit") or "").strip()

        parts = []
        qty_str = None
        if q is not None:
            qty_str = str(int(q)) if float(q).is_integer() else str(q)
            parts.append(qty_str)
        if u:
            parts.append(u)
        if name:
            parts.append(name)
        line = BULLET + " ".join([p for p in parts if p]) + "\n"
        start_line = cursor
        lines.append(line)

        pos = start_line + len(BULLET)

        if qty_str:
            q_start = pos
            q_end = q_start + len(qty_str)
            spans.append((q_start, q_end, "QTY"))
            pos = q_end + (1 if line[q_end:q_end+1] == " " else 0)

        if u:
            unit_token = u
            u_rel = line.find(unit_token, pos - start_line, len(line))
            if u_rel != -1:
                u_start = start_line + u_rel
                u_end = u_start + len(unit_token)
                spans.append((u_start, u_end, "UNIT"))
                pos = u_end + (1 if line[u_end:u_end+1] == " " else 0)

        if name:
            name_rel = line.find(name, pos - start_line, len(line))
            if name_rel != -1:
                name_start = start_line + name_rel
                name_end = name_start + len(name)
                spans.append((name_start, name_end, "INGREDIENT"))

        cursor += len(line)

    text = "".join(lines)
    return text, spans


def spans_to_bio(text: str, spans: List[Tuple[int,int,str]], tokenizer, max_len=256):
    enc = tokenizer(text, truncation=True, padding="max_length", max_length=max_len, return_offsets_mapping=True)
    offsets = enc["offset_mapping"]
    label2id = {t:i for i,t in enumerate(NER_TAGS)}
    labels = [label2id["O"]] * len(offsets)

    for (s, e, lab) in spans:
        for i, (a, b) in enumerate(offsets):
            if a == b:
                continue
            if b <= s or a >= e:
                continue
            labels[i] = label2id["B-" + lab] if a == s else label2id["I-" + lab]

    word_ids = enc.word_ids()
    final = []
    prev_w = None
    for i, wid in enumerate(word_ids):
        if wid is None:
            final.append(-100)
            continue
        if wid != prev_w:
            final.append(labels[i])
            prev_w = wid
        else:
            final.append(-100)

    enc.pop("offset_mapping", None)
    return enc["input_ids"], enc["attention_mask"], final


def load_rows():
    rows = []
    for name in ["kaggle_food_recipes.jsonl","recipe_nlg.jsonl"]:
        p = os.path.join(DATA_IN, name)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                rows.extend(json.loads(x) for x in f)
    if not rows:
        raise SystemExit("No normalized data found. Run `python scripts/download_and_normalize.py` first.")
    return rows


def load_aug():
    aug = []
    if os.path.exists(AUG_PATH):
        with open(AUG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    if "text" in obj and "spans" in obj:
                        aug.append(obj)
                except json.JSONDecodeError:
                    continue
    return aug


def build_ner_dataset(rows, tokenizer, max_len=256, aug_examples=None):
    input_ids, attention_mask, labels = [], [], []
    for r in rows:
        ings = r.get("ingredients_struct") or []
        if not ings:
            continue
        text, spans = build_ingredient_lines(ings)
        ids, mask, lab = spans_to_bio(text, spans, tokenizer, max_len)
        input_ids.append(ids)
        attention_mask.append(mask)
        labels.append(lab)
    if aug_examples:
        for example in aug_examples:
            spans = [(int(s), int(e), str(l)) for s, e, l in example.get("spans", [])]
            if not spans:
                continue
            ids, mask, lab = spans_to_bio(example["text"], spans, tokenizer, max_len)
            input_ids.append(ids)
            attention_mask.append(mask)
            labels.append(lab)
    feats = Features({
        "input_ids": Sequence(Value("int64")),
        "attention_mask": Sequence(Value("int64")),
        "labels": Sequence(Value("int64")),
    })
    ds = Dataset.from_dict({"input_ids":input_ids,"attention_mask":attention_mask,"labels":labels}, features=feats)
    return ds, {t:i for i,t in enumerate(NER_TAGS)}


def build_cls_dataset(rows, tokenizer, max_len=128):
    texts = []
    labels = []
    for r in rows:
        t = (r.get("title") or "") + " " + (r.get("text") or "")
        texts.append(t.strip() or "recipe")
        labels.append(CLS_LABELS["flexible"])
    enc = tokenizer(texts, truncation=True, padding="max_length", max_length=max_len)
    feats = Features({
        "input_ids": Sequence(Value("int64")),
        "attention_mask": Sequence(Value("int64")),
        "labels": Value("int64"),
    })
    ds = Dataset.from_dict({"input_ids":enc["input_ids"],"attention_mask":enc["attention_mask"],"labels":labels}, features=feats)
    return ds, CLS_LABELS


if __name__ == "__main__":
    set_seed(42)
    tok = AutoTokenizer.from_pretrained(BASE_MODEL)

    rows = load_rows()
    aug_examples = load_aug()
    ner_ds, ner_map = build_ner_dataset(rows, tok, aug_examples=aug_examples)
    cls_ds, cls_map = build_cls_dataset(rows, tok)

    ner_ds.save_to_disk(os.path.join(CACHE_DIR, "ner"))
    cls_ds.save_to_disk(os.path.join(CACHE_DIR, "cls"))
    save_json(ner_map, os.path.join(META_DIR, "ner_label2id.json"))
    save_json({v:k for k,v in ner_map.items()}, os.path.join(META_DIR, "ner_id2label.json"))
    save_json(cls_map, os.path.join(META_DIR, "cls_label2id.json"))
    print(f"NER samples: {len(ner_ds)} | CLS samples: {len(cls_ds)}")
