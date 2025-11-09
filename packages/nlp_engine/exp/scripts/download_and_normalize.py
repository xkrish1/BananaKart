import json, os, re, math
from typing import List, Dict, Optional
from datasets import load_dataset
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "normalized")
os.makedirs(OUT_DIR, exist_ok=True)

CANDIDATE_ING_COLS = [
    "ingredients", "Ingredients", "ingredient", "Ingredient",
    "Cleaned_Ingredients", "cleaned_ingredients", "NER", "RecipeIngredientParts"
]

def split_ingredient_line(s: str) -> List[str]:
    if not isinstance(s, str):
        return []
    # try JSON-ish lists
    s_strip = s.strip()
    if s_strip.startswith("[") and s_strip.endswith("]"):
        try:
            arr = json.loads(s_strip)
            return [str(x).strip() for x in arr if str(x).strip()]
        except Exception:
            pass
    # fallback: split on commas or semicolons
    parts = re.split(r"[;,]\s*", s)
    return [p.strip() for p in parts if p.strip()]

QTY_RE = re.compile(
    r"(?P<num>(?:\d+[\d/\.\-]*|\d*\s*\d+/\d+|\d+\.?\d*))\s*(?P<unit>[a-zA-Zµ]+\.?)?",
    flags=re.IGNORECASE,
)

def parse_qty_unit(text: str) -> (Optional[float], Optional[str]):
    if not isinstance(text, str): return None, None
    m = QTY_RE.search(text)
    if not m: return None, None
    raw_num = m.group("num").replace(" ", "")
    # handle unicode fractions like ½ ¼ ¾
    frac_map = {"½":"1/2","¼":"1/4","¾":"3/4","⅓":"1/3","⅔":"2/3","⅛":"1/8","⅜":"3/8","⅝":"5/8","⅞":"7/8"}
    for k,v in frac_map.items():
        raw_num = raw_num.replace(k, v)
    try:
        if "/" in raw_num:
            if raw_num.count("/") == 1:
                a,b = raw_num.split("/")
                val = float(a) / float(b)
            else:
                # e.g., 1-1/2 or 1+1/2 -> normalize non-digits
                parts = re.split(r"[^\d/]+", raw_num)
                nums = [p for p in parts if p]
                if len(nums) == 2:
                    val = float(nums[0]) / float(nums[1])
                elif len(nums) == 3:
                    val = float(nums[0]) + (float(nums[1]) / float(nums[2]))
                else:
                    val = None
        else:
            val = float(raw_num)
    except Exception:
        val = None
    unit = m.group("unit")
    if unit: unit = unit.lower().strip(".")
    return val, unit

def to_structured(ings: List[str]) -> List[Dict]:
    out = []
    for ing in ings:
        q, u = parse_qty_unit(ing)
        # remove qty+unit tokens from name if we captured them
        name = ing
        if q is not None:
            name = re.sub(QTY_RE, "", name, count=1).strip(", -")
        # normalize conjunction “and”
        name = re.sub(r"\band\b", ",", name)
        # split compound “walnuts and pecans”
        pieces = [p.strip() for p in re.split(r"[,/]", name) if p.strip()]
        if len(pieces) > 1 and q is not None and u:
            # replicate qty/unit for each
            for p in pieces:
                out.append({"name": p, "quantity": q, "unit": u, "raw": ing})
        else:
            out.append({"name": name, "quantity": q, "unit": u, "raw": ing})
    # drop empties
    return [x for x in out if x["name"]]

def guess_ing_col(cols: List[str]) -> Optional[str]:
    lower = {c.lower(): c for c in cols}
    for c in CANDIDATE_ING_COLS:
        if c.lower() in lower: return lower[c.lower()]
    # heuristic: pick first column that contains “ingre”
    for c in cols:
        if "ingre" in c.lower(): return c
    return None

def normalize_kaggle_food_recipes(limit: Optional[int] = None):
    ds = load_dataset("Hieu-Pham/kaggle_food_recipes", split="train")
    df = ds.to_pandas()
    col = guess_ing_col(list(df.columns))
    if not col:
        raise RuntimeError(f"No ingredient column found. Columns: {list(df.columns)}")
    rows = []
    for _, r in df.iterrows():
        title = r.get("Title") or r.get("title") or r.get("RecipeName") or ""
        text = r.get("Instructions") or r.get("directions") or r.get("Cooked_Directions") or ""
        ing_field = r.get(col)
        items = split_ingredient_line(ing_field)
        rows.append({
            "title": str(title) if not pd.isna(title) else "",
            "text": str(text) if not pd.isna(text) else "",
            "ingredients_raw": items,
            "ingredients_struct": to_structured(items),
            "source": "Hieu-Pham/kaggle_food_recipes"
        })
    if limit is not None:
        rows = rows[:limit]

    out_path = os.path.join(OUT_DIR, "kaggle_food_recipes.jsonl")
    with open(out_path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Wrote {len(rows)} rows to {out_path}")

def normalize_recipe_nlg(limit: Optional[int] = None):
    # RecipeNLG on HF mirrors include ingredients field; load default split
    ds = load_dataset("mbien/recipe_nlg", split="train")
    df = ds.to_pandas()
    # common columns in RecipeNLG mirrors: 'title','ingredients','directions'
    cand = [c for c in df.columns if "ingredient" in c.lower()]
    if not cand:
        raise RuntimeError(f"No ingredients column detected. Columns: {list(df.columns)}")
    col = cand[0]
    rows = []
    for _, r in df.iterrows():
        title = r.get("title") or ""
        text = r.get("directions") or r.get("instructions") or ""
        items = split_ingredient_line(r.get(col))
        rows.append({
            "title": str(title) if not pd.isna(title) else "",
            "text": str(text) if not pd.isna(text) else "",
            "ingredients_raw": items,
            "ingredients_struct": to_structured(items),
            "source": "mbien/recipe_nlg"
        })
    if limit is not None:
        rows = rows[:limit]

    out_path = os.path.join(OUT_DIR, "recipe_nlg.jsonl")
    with open(out_path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Wrote {len(rows)} rows to {out_path}")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", choices=["kaggle", "recipenlg", "both"], default="kaggle")
    p.add_argument("--limit", type=int, default=None, help="Optionally limit the number of rows processed per dataset.")
    args = p.parse_args()
    if args.dataset in ("kaggle", "both"):
        normalize_kaggle_food_recipes(limit=args.limit)
    if args.dataset in ("recipenlg", "both"):
        normalize_recipe_nlg(limit=args.limit)
