"""Environment loader for BananaKart backend."""
from __future__ import annotations

import os
import sys
from typing import Iterable

from dotenv import load_dotenv

REQUIRED_ENV_VARS: Iterable[str] = (
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
)


def load_env() -> None:
    """Load environment variables and validate required keys."""
    load_dotenv()

    missing = [key for key in REQUIRED_ENV_VARS if not os.getenv(key)]
    if missing:
        sys.exit(f"Missing required environment variables: {', '.join(missing)}")

    print("Loaded environment:")
    for key in REQUIRED_ENV_VARS:
        value = os.getenv(key, "")
        redacted = f"{value[:4]}{'•' * 12}" if value else "<empty>"
        print(f"  {key}={redacted}")


__all__ = ["load_env"]
