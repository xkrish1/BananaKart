"""Utility to debug BananaKart FastAPI import paths."""
from __future__ import annotations

import importlib
import pkgutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print("Python path entries:")
for entry in sys.path:
    print(f"  - {entry}")

print("\nLoading routes...")
try:
    analyze = importlib.import_module("apps.backend.routes.analyze")
    simulate = importlib.import_module("apps.backend.routes.simulate")
    print("  ✔ Successfully imported analyze and simulate routes.")
except Exception as exc:  # pylint: disable=broad-except
    print(f"  ✘ Failed to import routes: {exc}")
    raise

print("\nRegistered modules under 'apps.backend':")
for module in sorted(name for _, name, _ in pkgutil.walk_packages([str(PROJECT_ROOT / "apps" / "backend")], prefix="apps.backend.")):
    print(f"  - {module}")

print("\nCurrently loaded modules:")
for name in sorted(sys.modules):
    if name.startswith("apps.backend"):
        print(f"  - {name}")
