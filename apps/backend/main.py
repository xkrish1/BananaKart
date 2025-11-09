import logging
import os
import random
import traceback
from collections import defaultdict, deque
from time import time
from typing import Any, Deque, Dict, Optional

import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from services.supabase_client import insert_eco_result, insert_recipe
from routes import auto

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))
logger = logging.getLogger(__name__)

allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if allowed_origins_env:
    ALLOWED_ORIGINS = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
else:
    ALLOWED_ORIGINS = ["*"]

RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
_REQUEST_LOG: Dict[str, Deque[float]] = defaultdict(deque)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if RATE_LIMIT <= 0:
        return await call_next(request)

    client_host = request.client.host if request.client else "unknown"
    now = time()
    window_start = now - 60
    bucket = _REQUEST_LOG[client_host]

    while bucket and bucket[0] < window_start:
        bucket.popleft()

    if len(bucket) >= RATE_LIMIT:
        logger.warning("Rate limit exceeded for %s", client_host)
        return JSONResponse(status_code=429, content={"error": "rate limit exceeded"})

    bucket.append(now)
    return await call_next(request)


app.include_router(auto.router)

HF_MODEL = "xkrish/urgency-classifier-distilbert"
HF_API_KEY = os.getenv("HF_API_KEY")


def _call_hf_inference(recipe_text: str) -> Optional[float]:
    if not HF_API_KEY:
        return None

    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{HF_MODEL}",
            headers={"Authorization": f"Bearer {HF_API_KEY}"},
            json={"inputs": recipe_text},
            timeout=10,
        )
        response.raise_for_status()
        payload: Any = response.json()
        if isinstance(payload, list) and payload:
            first_item: Any = payload[0]
            if isinstance(first_item, list) and first_item:
                return float(first_item[0].get("score", 0.0))
            if isinstance(first_item, dict):
                return float(first_item.get("score", 0.0))
        elif isinstance(payload, dict):
            return float(payload.get("score", 0.0))
    except Exception as exc:  # pylint: disable=broad-except
        print("Hugging Face call failed:", exc)
        traceback.print_exc()
    return None


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
        # Step 1: Hugging Face inference
        try:
            model_score = _call_hf_inference(data.recipe_text)
        except Exception as exc:  # pylint: disable=broad-except
            print("HF inference failed:", exc)
            model_score = None
        score = model_score if model_score is not None else 0.8

        # Step 2: Monte Carlo simulation
        eco_score = round(score * random.uniform(0.85, 0.95), 2)
        co2_saved_kg = round(eco_score * 1.75, 2)
        variance_cost = 0.1
        best_sources = ["local-market", "organic-farm"]
        route_cluster = random.choice(["urban", "suburban", "rural"])

        # Step 3: Supabase insertion
        recipe_record = insert_recipe(data.user_id, data.recipe_text, data.urgency)
        recipe_id: Optional[str] = recipe_record.get("id") if isinstance(recipe_record, dict) else None
        if recipe_id:
            insert_eco_result(
                recipe_id=recipe_id,
                eco_score=eco_score,
                co2_saved_kg=co2_saved_kg,
                variance_cost=variance_cost,
                best_sources=best_sources,
                route_cluster=route_cluster,
            )

        return {
            "status": "ok",
            "eco_score": eco_score,
            "co2_saved": co2_saved_kg,
            "variance_cost": variance_cost,
            "recipe_id": recipe_id,
        }

    except Exception as exc:  # pylint: disable=broad-except
        print("Unexpected error:", exc)
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(exc)
        }
