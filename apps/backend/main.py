from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class RecipeInput(BaseModel):
    user_id: str
    recipe_text: str
    urgency: str


@app.post("/analyze")
def analyze_recipe(data: RecipeInput):
    return {
        "status": "ok",
        "received": data.model_dump(),
        "eco_score": 0.82,
        "co2_saved": 2.3,
        "variance_cost": 0.11
    }
