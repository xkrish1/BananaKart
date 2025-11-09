from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, requests, random, traceback
from supabase_client import insert_recipe, insert_eco_result

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = "distilbert-base-uncased"   # can be your own uploaded model


class RecipeInput(BaseModel):
    user_id: str
    recipe_text: str
    urgency: str


@app.get("/")
def root():
    return {"status": "ok", "message": "BananaKart backend with Hugging Face API"}


@app.post("/analyze")
def analyze_recipe(data: RecipeInput):
    try:
        # --- Hugging Face inference ---
        score = 0.8
        if HF_API_KEY:
            try:
                res = requests.post(
                    f"https://api-inference.huggingface.co/models/{HF_MODEL}",
                    headers={"Authorization": f"Bearer {HF_API_KEY}"},
                    json={"inputs": data.recipe_text},
                    timeout=10
                )
                payload = res.json()
                if isinstance(payload, list) and isinstance(payload[0], list):
                    score = float(payload[0][0].get("score", 0.8))
                elif isinstance(payload, list) and isinstance(payload[0], dict):
                    score = float(payload[0].get("score", 0.8))
            except Exception as e:
                print("Hugging Face call failed:", e)
                traceback.print_exc()
                score = 0.8

        # --- Simulate Monte Carlo ---
        eco_score = round(score * 0.9, 2)
        co2_saved = round(eco_score * 2.0, 2)
        variance_cost = 0.1

        # --- Supabase inserts ---
        recipe_id = None
        try:
            recipe_id = insert_recipe(data.user_id, data.recipe_text, data.urgency)
            insert_eco_result(recipe_id, eco_score, co2_saved, variance_cost)
        except Exception as e:
            print("Supabase insert failed:", e)
            traceback.print_exc()

        return {
            "status": "ok",
            "eco_score": eco_score,
            "co2_saved": co2_saved,
            "variance_cost": variance_cost,
            "recipe_id": recipe_id
        }

    except Exception as e:
        print("Unexpected error:", e)
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e)
        }
