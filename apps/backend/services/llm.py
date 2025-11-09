"""LLM helper for recipe generation via OpenAI (mock-friendly)."""
from __future__ import annotations

import json
import os
from typing import Any, Dict

import requests

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


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
    """Call OpenAI's chat API to generate a structured recipe.

    Falls back to a deterministic mock if the API key is missing or the call fails.
    """

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _fallback_recipe(query, servings)

    prompt = _build_prompt(query, servings)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": "You return only valid JSON."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 600,
    }

    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        recipe = json.loads(content)
        if not isinstance(recipe, dict):
            raise ValueError("Unexpected recipe payload")
        recipe.setdefault("servings", servings)
        return recipe
    except Exception:
        return _fallback_recipe(query, servings)
