import os
from dotenv import load_dotenv
from supabase import create_client


load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def insert_recipe(user_id: str, recipe_text: str, urgency: str):
    response = supabase.table("recipes").insert({
        "user_id": user_id,
        "text": recipe_text,
        "urgency": urgency
    }).execute()
    return response.data[0]["id"]


def insert_eco_result(recipe_id: str, eco_score: float, co2_saved: float, variance_cost: float):
    supabase.table("eco_results").insert({
        "recipe_id": recipe_id,
        "eco_score": eco_score,
        "co2_saved": co2_saved,
        "variance_cost": variance_cost
    }).execute()

