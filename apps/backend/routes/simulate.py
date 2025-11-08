"""Simulation routes for eco impact calculations."""
from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from packages.simulation_engine.montecarlo import run_simulation
from ..services.supabase_client import insert_eco_result

router = APIRouter()


class SimulationRequest(BaseModel):
    recipe_id: UUID = Field(..., description="Recipe identifier to simulate")


class SimulationResponse(BaseModel):
    eco_score: float
    co2_saved_kg: float
    variance_cost: float
    best_sources: list[str]
    route_cluster: str


@router.post("", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
async def simulate_recipe(payload: SimulationRequest) -> JSONResponse:
    """Run the Monte Carlo simulation and persist eco results."""
    try:
        result: Dict[str, Any] = run_simulation(str(payload.recipe_id))
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Simulation failed: {exc}") from exc

    required_keys = {"eco_score", "co2_saved_kg", "variance_cost", "best_sources", "route_cluster"}
    if not required_keys.issubset(result):
        missing = required_keys.difference(result)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Simulation result missing keys: {sorted(missing)}")

    try:
        insert_eco_result(
            recipe_id=str(payload.recipe_id),
            eco_score=float(result["eco_score"]),
            co2_saved=float(result["co2_saved_kg"]),
            variance_cost=float(result["variance_cost"]),
            best_sources=list(result["best_sources"]),
            route_cluster=str(result["route_cluster"]),
        )
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to store eco result: {exc}") from exc

    response = SimulationResponse(**{key: result[key] for key in required_keys})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=response.dict())
