"""Route that combines LLM recipe generation with farmers market lookup."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, PositiveInt, constr

from apps.backend.services.llm import generate_recipe
from apps.backend.services.farmers_markets import find_markets

router = APIRouter(prefix="/llm_recipe", tags=["llm"])


class RecipeRequest(BaseModel):
    text: constr(strip_whitespace=True, min_length=3)
    servings: PositiveInt = Field(default=2)
    zipcode: constr(strip_whitespace=True, min_length=3, max_length=10) = Field(
        ..., description="ZIP code or prefix used to find farmers markets"
    )


class Ingredient(BaseModel):
    name: Optional[str]
    quantity: Optional[float]
    unit: Optional[str]


class RecipeResponse(BaseModel):
    title: str
    servings: PositiveInt
    ingredients: List[Ingredient]
    steps: List[str]


class LLMRecipeResponse(BaseModel):
    recipe: RecipeResponse
    farmers_markets: List[dict]


@router.post("", response_model=LLMRecipeResponse, status_code=status.HTTP_200_OK)
async def create_recipe(payload: RecipeRequest) -> LLMRecipeResponse:
    recipe_raw = generate_recipe(payload.text, payload.servings)
    if not isinstance(recipe_raw, dict) or "ingredients" not in recipe_raw:
        raise HTTPException(status_code=500, detail="Recipe generator returned invalid payload")

    recipe = RecipeResponse(
        title=recipe_raw.get("title", payload.text.title()),
        servings=recipe_raw.get("servings", payload.servings),
        ingredients=[Ingredient(**item) for item in recipe_raw.get("ingredients", [])],
        steps=[str(step) for step in recipe_raw.get("steps", [])],
    )

    markets = find_markets(payload.zipcode, limit=5)
    return LLMRecipeResponse(recipe=recipe, farmers_markets=markets)
