"""Supabase integration helpers with graceful fallbacks."""
from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

logger = logging.getLogger(__name__)

try:
    from supabase import Client, create_client  # type: ignore

    _IMPORT_ERROR: Optional[ModuleNotFoundError] = None
except ModuleNotFoundError as exc:  # pragma: no cover - depends on deployment
    Client = Any  # type: ignore[assignment]
    create_client = None  # type: ignore[assignment]
    _IMPORT_ERROR = exc

REQUIRED_ENV_VARS = ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY")


class SupabaseDependencyError(RuntimeError):
    """Raised when the Supabase Python SDK is not installed."""


class SupabaseConfigError(RuntimeError):
    """Raised when required Supabase environment variables are missing."""


@runtime_checkable
class SupportsTable(Protocol):
    """Subset of supabase.Client used by the backend."""

    def table(self, name: str) -> Any:  # pragma: no cover - protocol definition
        ...


def _check_dependency() -> None:
    if _IMPORT_ERROR is not None or create_client is None:  # pragma: no cover - env dependent
        raise SupabaseDependencyError(
            "Supabase client library is not installed. "
            "Install dependencies with `pip install -r apps/backend/requirements.txt` "
            "or activate the project's virtual environment."
        ) from _IMPORT_ERROR


def _get_credentials() -> tuple[str, str]:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        missing = [name for name, value in zip(REQUIRED_ENV_VARS, (url, key)) if not value]
        raise SupabaseConfigError(
            "Missing Supabase configuration: "
            f"{', '.join(missing)}. Ensure these environment variables are set."
        )
    return url, key


@lru_cache(maxsize=1)
def _create_client() -> SupportsTable:
    _check_dependency()
    url, key = _get_credentials()
    return create_client(url, key)  # type: ignore[misc]


def get_client(raise_on_error: bool = False) -> Optional[SupportsTable]:
    """Return the cached Supabase client or None when unavailable."""
    try:
        return _create_client()
    except (SupabaseDependencyError, SupabaseConfigError) as exc:
        logger.warning("Supabase client unavailable: %s", exc)
        if raise_on_error:
            raise
    return None


def insert_recipe(user_id: str, recipe_text: str, urgency: str) -> Optional[Dict[str, Any]]:
    client = get_client()
    if client is None:
        logger.info("Skipping recipe insert because Supabase client is unavailable.")
        return None

    response = (
        client.table("recipes")
        .insert(
            {
                "user_id": user_id,
                "recipe_text": recipe_text,
                "urgency": urgency,
            }
        )
        .execute()
    )
    return response.data[0] if getattr(response, "data", None) else None


def insert_eco_result(
    recipe_id: str,
    eco_score: float,
    co2_saved_kg: float,
    variance_cost: float,
    best_sources: List[str],
    route_cluster: str,
) -> Optional[Dict[str, Any]]:
    client = get_client()
    if client is None:
        logger.info("Skipping eco result insert because Supabase client is unavailable.")
        return None

    response = (
        client.table("eco_results")
        .insert(
            {
                "recipe_id": recipe_id,
                "eco_score": eco_score,
                "co2_saved_kg": co2_saved_kg,
                "variance_cost": variance_cost,
                "best_sources": best_sources,
                "route_cluster": route_cluster,
            }
        )
        .execute()
    )
    return response.data[0] if getattr(response, "data", None) else None


supabase = get_client()

__all__ = [
    "SupabaseConfigError",
    "SupabaseDependencyError",
    "get_client",
    "insert_eco_result",
    "insert_recipe",
    "supabase",
]
