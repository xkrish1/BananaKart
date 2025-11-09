import os
import uuid
import traceback
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from supabase import Client, create_client


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in the environment.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)



def insert_recipe(user_id: str, recipe_text: str, urgency: str) -> Dict[str, Any]:
    try:
        try:
            uuid.UUID(user_id)
        except Exception:
            user_id = str(uuid.uuid4())

        supabase.table("users").upsert(
            {
                "id": user_id,
                "email": f"{user_id[:6]}@demo.bananakart.ai",
            }
        ).execute()

        result = (
            supabase.table("recipes")
            .insert(
                {
                    "user_id": user_id,
                    "recipe_text": recipe_text,
                    "urgency": urgency,
                }
            )
            .execute()
        )
        return result.data[0] if result.data else {}
    except Exception as exc:  # pylint: disable=broad-except
        print("Error inserting recipe:", exc)
        traceback.print_exc()
        return {}


def insert_eco_result(
    recipe_id: str,
    eco_score: float,
    co2_saved_kg: float,
    variance_cost: float,
    best_sources: List[str],
    route_cluster: str,
) -> Optional[Dict[str, Any]]:
    """Insert an eco result row and return the inserted record."""
    try:
        response = (
            supabase.table("eco_results")
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
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error inserting eco result: {exc}")
        traceback.print_exc()
        return None

