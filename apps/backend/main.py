from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
from supabase_client import insert_recipe, insert_eco_result

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RecipeInput(BaseModel):
    user_id: str
    recipe_text: str
    urgency: str


# Load DistilBERT model
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased")


@app.get("/")
def root():
    return {"status": "ok", "message": "BananaKart backend with Supabase + NLP + Monte Carlo"}


@app.post("/analyze")
def analyze_recipe(data: RecipeInput):
    tokens = tokenizer(data.recipe_text, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**tokens)
    score = torch.softmax(outputs.logits, dim=1)[0][1].item()

    # Simple Monte Carlo simulation (1000 samples)
    costs = np.random.normal(10, 2, 1000)
    emissions = np.random.normal(5, 1, 1000)
    eco_score = round((1 - np.mean(emissions) / 10) * score, 2)
    co2_saved = round(np.mean(emissions) * 0.1, 2)
    variance_cost = round(np.var(costs) / 100, 2)

    # Insert into Supabase
    recipe_id = insert_recipe(data.user_id, data.recipe_text, data.urgency)
    insert_eco_result(recipe_id, eco_score, co2_saved, variance_cost)

    return {
        "status": "ok",
        "recipe_id": recipe_id,
        "eco_score": eco_score,
        "co2_saved": co2_saved,
        "variance_cost": variance_cost
    }
