import json
import os
import random

p = os.path.join(os.path.dirname(__file__), "..", "data", "normalized", "kaggle_food_recipes.jsonl")
n = 20

with open(p, "r", encoding="utf-8") as f:
    rows = [json.loads(x) for x in f]

for r in random.sample(rows, min(n, len(rows))):
    print(r.get("title", "")[:60])
    for ing in r.get("ingredients_struct", [])[:8]:
        print(" -", ing)
    print()
