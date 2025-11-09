"""LLM helper for recipe generation via Gemini (mock-friendly)."""
from __future__ import annotations

import json
import os
from typing import Any, Dict

import requests

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")


def _build_prompt(query: str, servings: int) -> str:
    return (
        "You are an expert chef. Generate a recipe in strict JSON format with keys: "
        "title (string), servings (int), ingredients (array of {name, quantity, unit}), "
        "steps (array of strings). The recipe should satisfy the request: "
        f"'{query}' for {servings} servings. JSON only, no prose."
    )


def _fallback_recipe(query: str, servings: int) -> Dict[str, Any]:
    title = query.strip().title() if query else "Chef's Choice"
    return {
        "title": title,
        "servings": servings,
        "ingredients": [
            {"name": "seasonal vegetables", "quantity": 2, "unit": "cups"},
            {"name": "olive oil", "quantity": 2, "unit": "tbsp"},
            {"name": "salt", "quantity": 1, "unit": "tsp"},
        ],
        "steps": [
            "Heat olive oil in a skillet.",
            "Add vegetables and sauté until tender.",
            "Season with salt and serve warm.",
        ],
    }


def generate_recipe(query: str, servings: int = 1) -> Dict[str, Any]:
    """Call Gemini's API to generate a structured recipe.

    Falls back to a deterministic mock if the API key is missing or the call fails.
    """

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _fallback_recipe(query, servings)

    prompt = _build_prompt(query, servings)
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": "You return only valid JSON."}, {"text": prompt}],
            }
        ],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 600},
    }

    try:
        url = GEMINI_API_URL.format(model=GEMINI_MODEL)
        response = requests.post(url, headers=headers, params={"key": api_key}, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        candidates = data.get("candidates") or []
        if not candidates:
            raise ValueError("No candidates returned from Gemini")
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            raise ValueError("Gemini response missing parts")
        content = parts[0].get("text", "")
        recipe = json.loads(content)
        if not isinstance(recipe, dict):
            raise ValueError("Unexpected recipe payload")
        recipe.setdefault("servings", servings)
        return recipe
    except Exception:
        return _fallback_recipe(query, servings)
