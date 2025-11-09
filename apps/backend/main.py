from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Enable CORS for all origins
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


@app.get("/")
def root():
    return {"status": "ok", "message": "BananaKart backend running"}


@app.post("/analyze")
def analyze_recipe(data: RecipeInput):
    return {
        "status": "ok",
        "received": data.model_dump(),
        "eco_score": 0.84,
        "co2_saved": 2.1,
        "variance_cost": 0.12
    }
