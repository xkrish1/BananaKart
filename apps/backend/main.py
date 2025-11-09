from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, requests, random
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
            # Some models return nested arrays
            if isinstance(payload, list) and isinstance(payload[0], list):
                score = float(payload[0][0].get("score", 0.8))
        except Exception as e:
            print("HF call failed:", e)
            score = round(random.uniform(0.7, 0.9), 2)

    eco_score = round(score * 0.9, 2)
    co2_saved = round(eco_score * 2.0, 2)
    variance_cost = 0.1

    recipe_id = insert_recipe(data.user_id, data.recipe_text, data.urgency)
    insert_eco_result(recipe_id, eco_score, co2_saved, variance_cost)

    return {
        "status": "ok",
        "eco_score": eco_score,
        "co2_saved": co2_saved,
        "variance_cost": variance_cost,
        "recipe_id": recipe_id
    }
