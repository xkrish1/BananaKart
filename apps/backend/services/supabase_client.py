"""Supabase client utilities with memoization and legacy helpers."""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from supabase import Client, create_client

__all__ = ["get_client", "supabase", "insert_recipe", "insert_eco_result"]

_SUPABASE_CLIENT: Optional[Client] = None


def _create_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise RuntimeError("Supabase config missing")
    return create_client(url, key)


def get_client() -> Client:
    """Return a memoized Supabase client instance."""
    global _SUPABASE_CLIENT
    if _SUPABASE_CLIENT is None:
        _SUPABASE_CLIENT = _create_client()
    return _SUPABASE_CLIENT


def insert_recipe(user_id: str, recipe_text: str, urgency: str) -> Optional[Dict[str, Any]]:
    client = get_client()
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
    return response.data[0] if response.data else None


def insert_eco_result(
    recipe_id: str,
    eco_score: float,
    co2_saved_kg: float,
    variance_cost: float,
    best_sources: List[str],
    route_cluster: str,
) -> Optional[Dict[str, Any]]:
    client = get_client()
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
    return response.data[0] if response.data else None


try:
    supabase = get_client()
except RuntimeError:
    supabase = None
