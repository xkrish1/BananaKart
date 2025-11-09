import os
import sys
from pathlib import Path

os.environ.setdefault("USE_LOCAL_NLP", "true")

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.nlp_engine.parser import parse


def test_parse_smoke():
    output = parse("• 200 g penne\n• 2 tbsp olive oil")
    assert any("penne" in item.get("name", "").lower() for item in output["ingredients"])
    assert output["urgency"] in {"tonight", "this_week", "flexible"}
