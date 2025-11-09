"""Auto route that chooses between parsing and generation."""
from __future__ import annotations

import os
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, PositiveInt, constr

from packages.nlp_engine.parser import parse

from ..services.generator import generate_recipe

DEFAULT_SERVINGS = 1

router = APIRouter(prefix="/analyze_or_generate", tags=["auto"])


class IngredientOut(BaseModel):
    name: Optional[str]
    quantity: Optional[float]
    unit: Optional[str]


class AutoIn(BaseModel):
    text: constr(strip_whitespace=True, min_length=1) = Field(..., description="Recipe text or free-form query")
    servings: Optional[PositiveInt] = Field(default=None, description="Desired servings")


class AutoOut(BaseModel):
    mode: str
    title: Optional[str]
    servings: PositiveInt
    servings_assumed: bool
    ingredients: List[IngredientOut]
    steps: List[str]
    source: str
    model: Optional[str] = None
    urgency: Optional[str] = None
    meal_time: Optional[str] = None


@router.post("", status_code=status.HTTP_200_OK, response_model=AutoOut)
async def analyze_or_generate(payload: AutoIn) -> AutoOut:
    text = payload.text

    provided_servings = payload.servings
    default_servings = int(os.getenv("GEN_DEFAULT_SERVINGS", DEFAULT_SERVINGS))
    servings = int(provided_servings or default_servings)
    assumed = provided_servings is None

    lowered = text.lower()
    is_recipe = (
        len(text) >= 140
        or lowered.count("\n") >= 2
        or any(token in lowered for token in ["•", "- ", "* ", "ingredients", "directions", "instructions", "1.", "2."])
    )

    if is_recipe:
        parsed = parse(text)
        if not isinstance(parsed, dict):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Parser returned unexpected format")
        ingredients = []
        for item in parsed.get("ingredients", []):
            if isinstance(item, dict):
                ingredients.append(
                    {
                        "name": item.get("name"),
                        "quantity": item.get("quantity"),
                        "unit": item.get("unit"),
                    }
                )
        return AutoOut(
            mode="parse",
            title=None,
            servings=servings,
            servings_assumed=assumed,
            ingredients=ingredients,
            steps=[],
            source="extractor",
            model=None,
            urgency=parsed.get("urgency"),
            meal_time=parsed.get("meal_time"),
        )

    generated = generate_recipe(query=text, servings=servings, assumed=assumed)
    generated.setdefault("urgency", None)
    generated.setdefault("meal_time", None)
    return AutoOut(**generated)
