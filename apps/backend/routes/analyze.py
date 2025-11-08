"""Recipe analysis routes."""
from typing import Any, Dict, List, Tuple
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from packages.nlp_engine.parser import parse_recipe
from ..services.supabase_client import insert_recipe, supabase

router = APIRouter()


class AnalyzeRequest(BaseModel):
    user_id: UUID = Field(..., description="Supabase user identifier")
    recipe_text: str = Field(..., min_length=1, description="Raw recipe text to analyze")
    urgency: str = Field(..., pattern=r"^(tonight|soon|later)$", description="Desired recipe urgency")


class AnalyzeResponse(BaseModel):
    recipe_id: UUID
    ingredients: List[str]
    message: str


def _normalize_ingredient(item: Any) -> Tuple[str, Dict[str, Any]]:
    """Convert ingredient output into storage-ready payload."""
    if isinstance(item, dict):
        name = item.get("ingredient_name") or item.get("name") or item.get("ingredient")
        if not name:
            raise ValueError("Ingredient dictionary missing name field.")
        quantity = item.get("quantity", 1)
        unit = item.get("unit", "unit")
    else:
        name = str(item).strip()
        if not name:
            raise ValueError("Ingredient entry is empty.")
        quantity = 1
        unit = "unit"

    try:
        quantity_val = float(quantity)
    except (TypeError, ValueError) as exc:  # type: ignore[arg-type]
        raise ValueError("Ingredient quantity must be numeric.") from exc

    return (
        name,
        {
            "ingredient_name": name,
            "quantity": quantity_val,
            "unit": unit,
        },
    )


@router.post("", response_model=AnalyzeResponse, status_code=status.HTTP_201_CREATED)
async def analyze_recipe(payload: AnalyzeRequest) -> JSONResponse:
    """Analyze a recipe via NLP and persist results to Supabase."""
    try:
        parsed = parse_recipe(payload.recipe_text)
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"NLP parsing failed: {exc}") from exc

    if not isinstance(parsed, list):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Parser returned unexpected format.")

    try:
        normalized = [_normalize_ingredient(item) for item in parsed]
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    ingredient_names = [name for name, _ in normalized]

    try:
        recipe_rows = insert_recipe(str(payload.user_id), payload.recipe_text, payload.urgency)
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to store recipe: {exc}") from exc

    if not recipe_rows:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Recipe insert returned no data.")

    recipe_id = recipe_rows[0].get("id")
    if not recipe_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Recipe insert missing identifier.")

    ingredient_records = [
        {
            **record,
            "recipe_id": recipe_id,
        }
        for _, record in normalized
    ]

    if ingredient_records:
        try:
            supabase.table("ingredients").insert(ingredient_records).execute()
        except Exception as exc:  # pylint: disable=broad-except
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to store ingredients: {exc}") from exc

    response = AnalyzeResponse(
        recipe_id=recipe_id,
        ingredients=ingredient_names,
        message="Recipe analyzed and stored.",
    )
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=response.dict())
