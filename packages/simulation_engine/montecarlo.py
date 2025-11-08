"""Monte Carlo simulation utilities for BananaKart eco impact estimates."""
from __future__ import annotations

import os
import random
from typing import Dict, List

import numpy as np
import requests

CO2_FACTORS: Dict[str, float] = {"local": 0.1, "regional": 0.25, "big_box": 0.4}
BASE_PRICES: Dict[str, float] = {"local": 10.0, "regional": 8.0, "big_box": 6.0}
WEATHER_MULTIPLIERS: Dict[str, float] = {
    "Clear": 1.0,
    "Clouds": 1.05,
    "Rain": 1.15,
    "Snow": 1.25,
    "Extreme": 1.4,
}

OPENWEATHER_DEFAULT_KEY = "66bf6aa1abd8d50068b18ea218913a3e"
TOMTOM_DEFAULT_KEY = "AxPKmUFJCjqytquR1qi33SaXXQZmXlp3"
DEFAULT_LATITUDE = 42.3601
DEFAULT_LONGITUDE = -71.0589

API_TIMEOUT_SECONDS = 5

__all__ = ["run_simulation"]


def _get_env_float(name: str, default: float) -> float:
    """Fetch a float environment variable, falling back to ``default``."""
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


def get_weather_factor() -> float:
    """Fetch a weather adjustment factor from the OpenWeatherMap API."""
    api_key = os.getenv("OPENWEATHER_KEY", OPENWEATHER_DEFAULT_KEY)
    lat = _get_env_float("DEFAULT_LAT", DEFAULT_LATITUDE)
    lon = _get_env_float("DEFAULT_LON", DEFAULT_LONGITUDE)

    if not api_key:
        return 1.0

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": api_key}
    try:
        response = requests.get(url, params=params, timeout=API_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
        condition = (payload.get("weather") or [{}])[0].get("main")
        return WEATHER_MULTIPLIERS.get(condition, 1.0)
    except Exception:
        return 1.0


def get_traffic_factor() -> float:
    """Fetch a congestion multiplier from the TomTom Flow API."""
    api_key = os.getenv("TOMTOM_KEY", TOMTOM_DEFAULT_KEY)
    lat = _get_env_float("DEFAULT_LAT", DEFAULT_LATITUDE)
    lon = _get_env_float("DEFAULT_LON", DEFAULT_LONGITUDE)

    if not api_key:
        return 1.0

    url = "https://api.tomtom.com/traffic/services/4/flowSegmentData/relative0/10/json"
    params = {"point": f"{lat},{lon}", "key": api_key}
    try:
        response = requests.get(url, params=params, timeout=API_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
        flow_segment = payload.get("flowSegmentData", {})
        current_speed = flow_segment.get("currentSpeed")
        free_flow_speed = flow_segment.get("freeFlowSpeed")
        if not current_speed or not free_flow_speed:
            return 1.0
        ratio = free_flow_speed / current_speed if current_speed else 1.0
        return float(max(0.5, min(2.0, ratio)))
    except Exception:
        return 1.0


def _simulate_samples(n_samples: int, weather_factor: float, traffic_factor_global: float) -> Dict[str, np.ndarray]:
    """Run stochastic sampling and return per-sample arrays."""
    supplier_types: List[str] = list(CO2_FACTORS.keys())
    rng = np.random.default_rng()

    supplier_indices = rng.integers(0, len(supplier_types), size=n_samples)
    supplier_array = np.array(supplier_types)[supplier_indices]

    distances = rng.uniform(1.0, 50.0, size=n_samples)
    traffic_local = np.clip(rng.normal(loc=1.0, scale=0.1, size=n_samples), 0.5, 2.0)
    price_factor = np.clip(rng.normal(loc=1.0, scale=0.15, size=n_samples), 0.5, 2.0)

    co2_per_km = np.vectorize(CO2_FACTORS.get)(supplier_array)
    base_prices = np.vectorize(BASE_PRICES.get)(supplier_array)

    emissions = distances * co2_per_km * traffic_local * weather_factor * traffic_factor_global
    costs = base_prices * price_factor

    return {
        "suppliers": supplier_array,
        "emissions": emissions,
        "costs": costs,
    }


def _aggregate_best_suppliers(suppliers: np.ndarray, emissions: np.ndarray) -> List[str]:
    """Determine the best supplier types based on mean emissions."""
    results: Dict[str, float] = {}
    for supplier in CO2_FACTORS.keys():
        mask = suppliers == supplier
        if np.any(mask):
            results[supplier] = float(np.mean(emissions[mask]))
    if not results:
        return []

    sorted_suppliers = sorted(results.items(), key=lambda item: item[1])
    return [name for name, _ in sorted_suppliers[:2]]


def run_simulation(recipe_id: str, n_samples: int = 10000) -> Dict[str, object]:
    """Run the Monte Carlo simulation and produce eco impact metrics."""
    if n_samples <= 0:
        raise ValueError("n_samples must be a positive integer")

    _ = recipe_id  # Explicitly unused but kept for signature compatibility.

    weather_factor = get_weather_factor()
    traffic_factor_global = get_traffic_factor()

    samples = _simulate_samples(n_samples, weather_factor, traffic_factor_global)
    emissions = samples["emissions"]
    costs = samples["costs"]

    mean_co2 = float(np.mean(emissions)) if emissions.size else 0.0
    mean_cost = float(np.mean(costs)) if costs.size else 0.0
    std_cost = float(np.std(costs)) if costs.size else 0.0

    eco_score = 1.0 - (mean_co2 / (mean_co2 + 20.0)) if mean_co2 >= 0 else 0.0
    co2_saved = 50.0 - mean_co2
    variance_cost = (std_cost / mean_cost) if mean_cost else 0.0

    best_sources = _aggregate_best_suppliers(samples["suppliers"], emissions)

    return {
        "eco_score": round(float(eco_score), 4),
        "co2_saved_kg": round(float(co2_saved), 4),
        "variance_cost": round(float(variance_cost), 4),
        "best_sources": best_sources,
        "route_cluster": "Cluster-SimA",
    }


if __name__ == "__main__":  # pragma: no cover - debug usage only
    random.seed(42)
    print(run_simulation("demo"))
