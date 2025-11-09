"""Route that combines LLM recipe generation with farmers market and big box sourcing."""
from __future__ import annotations

from typing import Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, PositiveInt, constr

from apps.backend.services.llm import generate_recipe
from apps.backend.services.sourcing import allocate_ingredients

router = APIRouter(prefix="/llm_recipe", tags=["llm"])


class RecipeRequest(BaseModel):
    text: constr(strip_whitespace=True, min_length=3)
    servings: PositiveInt = Field(default=2)
    zipcode: Optional[constr(strip_whitespace=True, min_length=3, max_length=10)] = Field(
        default=None, description="ZIP code or prefix used to find farmers markets"
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


class MarketAllocation(BaseModel):
    market: Dict[str, object]
    items: List[Ingredient]


class StoreAllocation(BaseModel):
    store: Dict[str, object]
    items: List[Ingredient]


class SourcingPlan(BaseModel):
    farmers_markets: List[MarketAllocation]
    big_box: List[StoreAllocation]


class LLMRecipeResponse(BaseModel):
    response_type: Literal["need_zip", "ok"]
    message: str
    recipe: Optional[RecipeResponse] = None
    sourcing: Optional[SourcingPlan] = None


@router.post("", response_model=LLMRecipeResponse, status_code=status.HTTP_200_OK)
async def create_recipe(payload: RecipeRequest) -> LLMRecipeResponse:
    if not payload.zipcode:
        return LLMRecipeResponse(
            response_type="need_zip",
            message="Please provide your ZIP code so I can locate nearby farmers markets.",
        )

    recipe_raw = generate_recipe(payload.text, payload.servings)
    if not isinstance(recipe_raw, dict) or "ingredients" not in recipe_raw:
        raise HTTPException(status_code=500, detail="Recipe generator returned invalid payload")

    recipe = RecipeResponse(
        title=recipe_raw.get("title", payload.text.title()),
        servings=recipe_raw.get("servings", payload.servings),
        ingredients=[Ingredient(**item) for item in recipe_raw.get("ingredients", [])],
        steps=[str(step) for step in recipe_raw.get("steps", [])],
    )

    market_alloc, big_box_alloc, _ = allocate_ingredients(
        [item.dict() for item in recipe.ingredients],
        payload.zipcode,
    )

    sourcing = SourcingPlan(
        farmers_markets=[
            MarketAllocation(
                market=record["market"],
                items=[Ingredient(**item) for item in record["items"]],
            )
            for record in market_alloc
        ],
        big_box=[
            StoreAllocation(
                store=record["store"],
                items=[Ingredient(**item) for item in record["items"]],
            )
            for record in big_box_alloc
        ],
    )

    return LLMRecipeResponse(
        response_type="ok",
        message="Here is your recipe and sourcing plan.",
        recipe=recipe,
        sourcing=sourcing,
    )
