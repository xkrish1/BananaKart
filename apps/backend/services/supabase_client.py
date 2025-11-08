import logging
import os
from typing import Any, Dict, List, Optional

from supabase import Client, create_client

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_PROJECT_REF = None
if SUPABASE_URL:
    SUPABASE_PROJECT_REF = SUPABASE_URL.split("https://")[-1].split(".")[0]

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in the environment.")

if SUPABASE_PROJECT_REF:
    logger.info("Initializing Supabase client for project ref '%s'", SUPABASE_PROJECT_REF)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def insert_recipe(user_id: str, recipe_text: str, urgency: str) -> Optional[List[Dict[str, Any]]]:
    try:
        response = (
            supabase
            .table("recipes")
            .insert({
                "user_id": user_id,
                "recipe_text": recipe_text,
                "urgency": urgency,
            })
            .execute()
        )
        return response.data
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Error inserting recipe: %s", exc)
        return None


def insert_eco_result(
    recipe_id: str,
    eco_score: float,
    co2_saved: float,
    variance_cost: float,
    best_sources: List[str],
    route_cluster: str,
) -> Optional[List[Dict[str, Any]]]:
    try:
        response = (
            supabase
            .table("eco_results")
            .insert({
                "recipe_id": recipe_id,
                "eco_score": eco_score,
                "co2_saved_kg": co2_saved,
                "variance_cost": variance_cost,
                "best_sources": best_sources,
                "route_cluster": route_cluster,
            })
            .execute()
        )
        return response.data
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Error inserting eco result: %s", exc)
        return None


def get_user_recipes(user_id: str) -> Optional[List[Dict[str, Any]]]:
    try:
        response = (
            supabase
            .table("recipes")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
        return response.data
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Error fetching user recipes: %s", exc)
        return None


def get_results(recipe_id: str) -> Optional[List[Dict[str, Any]]]:
    try:
        response = (
            supabase
            .table("eco_results")
            .select("*")
            .eq("recipe_id", recipe_id)
            .execute()
        )
        return response.data
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Error fetching eco results: %s", exc)
        return None
