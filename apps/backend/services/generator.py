"""Recipe generation service backed by Hugging Face Inference API with Supabase caching."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from packages.nlp_engine.parser import parse

from .supabase_client import get_client

GEN_MODEL_DEFAULT = "mistralai/Mistral-7B-Instruct-v0.2"
GEN_MAX_TOKENS_DEFAULT = 400
GEN_TEMPERATURE_DEFAULT = 0.2
GEN_DEFAULT_SERVINGS = 1
GEN_CACHE_TTL_DAYS_DEFAULT = 7
REQUEST_TIMEOUT_DEFAULT = 20
HF_MAX_RETRIES_DEFAULT = 2
GEN_PROVIDER = "hf"


def _create_session() -> requests.Session:
    session = requests.Session()
    retry_total = int(os.getenv("HF_MAX_RETRIES", HF_MAX_RETRIES_DEFAULT))
    retry = Retry(
        total=retry_total,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


SESSION = _create_session()


def _request_timeout() -> float:
    try:
        return float(os.getenv("REQUEST_TIMEOUT_SECONDS", REQUEST_TIMEOUT_DEFAULT))
    except (TypeError, ValueError):
        return REQUEST_TIMEOUT_DEFAULT


def _get_env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def build_prompt(query: str, servings: int) -> str:
    template = (
        "You are a culinary assistant. Generate a recipe as JSON ONLY with the following schema: "
        '{"title": str, "servings": int, "ingredients": [{"name": str, "quantity": number|null, "unit": str|null}], "steps": [str, ...]}. '
        "Use concise ingredient names, realistic quantities for {servings} servings, prefer US customary units, "
        "and avoid brand names. Respond with valid JSON and nothing else. Query: {query}"
    )
    return template.format(query=query.strip(), servings=servings)


def _hf_call(prompt: str) -> str:
    model_id = os.getenv("GEN_MODEL", GEN_MODEL_DEFAULT)
    token = os.getenv("HF_API_TOKEN")
    if not token:
        raise RuntimeError("HF_API_TOKEN is required for generation")

    max_tokens = _get_env_int("GEN_MAX_TOKENS", GEN_MAX_TOKENS_DEFAULT)
    temperature = float(os.getenv("GEN_TEMPERATURE", GEN_TEMPERATURE_DEFAULT))

    url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "return_full_text": False,
        },
    }

    try:
        response = SESSION.post(url, headers=headers, json=payload, timeout=_request_timeout())
    except requests.RequestException as exc:
        raise RuntimeError(f"HF inference request failed: {exc}") from exc

    if response.status_code >= 400:
        snippet = response.text[:200]
        raise RuntimeError(f"HF inference failed ({response.status_code}): {snippet}")

    data = response.json()
    if isinstance(data, list) and data:
        generated = data[0]
        if isinstance(generated, dict) and "generated_text" in generated:
            return generated["generated_text"]
        if isinstance(generated, str):
            return generated
    if isinstance(data, dict) and "generated_text" in data:
        return data["generated_text"]
    if isinstance(data, str):
        return data
    raise RuntimeError("HF inference returned unexpected payload")


def _cache_lookup(key_hash: str, ttl_days: int) -> Optional[Dict[str, Any]]:
    try:
        client = get_client()
    except RuntimeError:
        return None

    threshold = (datetime.utcnow() - timedelta(days=ttl_days)).isoformat()
    try:
        response = (
            client.table("gen_cache")
            .select("response_json")
            .eq("key_hash", key_hash)
            .gte("created_at", threshold)
            .limit(1)
            .execute()
        )
    except Exception:  # pragma: no cover - cache failures fall back to live call
        return None
    if not response.data:
        return None
    return response.data[0].get("response_json")


def _cache_store(
    key_hash: str,
    query: str,
    servings: int,
    provider: str,
    model: str,
    response_json: Dict[str, Any],
) -> None:
    try:
        client = get_client()
    except RuntimeError:
        return
    payload = {
        "key_hash": key_hash,
        "query_text": query,
        "servings": servings,
        "provider": provider,
        "model": model,
        "response_json": response_json,
    }
    try:
        client.table("gen_cache").upsert(payload, on_conflict="key_hash").execute()
    except Exception:
        return


def merge_ingredients(gen_list: List[Dict[str, Any]], parsed: Dict[str, Any]) -> List[Dict[str, Any]]:
    parsed_items = parsed.get("ingredients") if isinstance(parsed, dict) else None
    parsed_map: Dict[str, Dict[str, Any]] = {}
    if isinstance(parsed_items, list):
        for item in parsed_items:
            if not isinstance(item, dict):
                continue
            name = (item.get("name") or "").strip()
            if not name:
                continue
            parsed_map[name.lower()] = {
                "name": name,
                "quantity": item.get("quantity"),
                "unit": item.get("unit"),
            }

    merged: List[Dict[str, Any]] = []
    seen = set()
    for source in gen_list or []:
        if not isinstance(source, dict):
            continue
        name = (source.get("name") or "").strip()
        if not name:
            continue
        key = name.lower()
        parsed_item = parsed_map.get(key)
        merged.append(
            {
                "name": parsed_item.get("name") if parsed_item else name,
                "quantity": parsed_item.get("quantity") if parsed_item and parsed_item.get("quantity") is not None else source.get("quantity"),
                "unit": parsed_item.get("unit") if parsed_item and parsed_item.get("unit") else source.get("unit"),
            }
        )
        seen.add(key)

    for key, item in parsed_map.items():
        if key in seen:
            continue
        merged.append(item)

    return merged


def _sanitize_ingredients(raw: Any) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    if not isinstance(raw, list):
        return items
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        name = (entry.get("name") or "").strip()
        if not name:
            continue
        quantity = entry.get("quantity")
        unit = entry.get("unit")
        try:
            quantity_val = float(quantity) if quantity is not None else None
        except (TypeError, ValueError):
            quantity_val = None
        items.append({"name": name, "quantity": quantity_val, "unit": unit})
    return items


def _sanitized_steps(raw: Any) -> List[str]:
    if isinstance(raw, list):
        return [str(step).strip() for step in raw if str(step).strip()]
    return []


def generate_recipe(query: str, servings: Optional[int], assumed: bool) -> Dict[str, Any]:
    if not query or not query.strip():
        raise ValueError("Query text is required")

    model_id = os.getenv("GEN_MODEL", GEN_MODEL_DEFAULT)
    ttl_days = _get_env_int("GEN_CACHE_TTL_DAYS", GEN_CACHE_TTL_DAYS_DEFAULT)
    effective_servings = servings or _get_env_int("GEN_DEFAULT_SERVINGS", GEN_DEFAULT_SERVINGS)

    cache_key_source = f"{query}|{effective_servings}|{GEN_PROVIDER}|{model_id}"
    key_hash = hashlib.sha256(cache_key_source.encode("utf-8")).hexdigest()

    cached = _cache_lookup(key_hash, ttl_days)
    if isinstance(cached, dict):
        return cached

    prompt = build_prompt(query, effective_servings)
    try:
        raw_output = _hf_call(prompt)
    except RuntimeError as exc:
        raise RuntimeError(f"Failed to generate recipe: {exc}") from exc

    for attempt in range(2):
        try:
            candidate = json.loads(raw_output)
            break
        except json.JSONDecodeError:
            if attempt == 0:
                prompt = f"{prompt}\nReturn VALID JSON only."
                raw_output = _hf_call(prompt)
            else:
                raise RuntimeError("Generator returned non-JSON payload") from None
    else:  # pragma: no cover - loop exhausts only when both attempts fail
        raise RuntimeError("Generator parsing failed")

    if not isinstance(candidate, dict):
        raise RuntimeError("Generator payload must be a JSON object")

    title = str(candidate.get("title") or query).strip()
    gen_servings = candidate.get("servings")
    try:
        gen_servings_int = int(gen_servings)
    except (TypeError, ValueError):
        gen_servings_int = effective_servings

    generator_ingredients = _sanitize_ingredients(candidate.get("ingredients"))
    steps = _sanitized_steps(candidate.get("steps"))

    bullet_lines = []
    for item in generator_ingredients:
        quantity = item.get("quantity")
        if isinstance(quantity, float) and quantity.is_integer():
            quantity = int(quantity)
        parts = [part for part in [quantity, item.get("unit"), item.get("name")] if part not in (None, "")]
        if not parts:
            continue
        bullet_lines.append("• " + " ".join(str(part) for part in parts))

    parsed_output = parse("\n".join(bullet_lines) if bullet_lines else query)
    merged_ingredients = merge_ingredients(generator_ingredients, parsed_output if isinstance(parsed_output, dict) else {})

    payload = {
        "mode": "generate",
        "title": title,
        "servings": gen_servings_int,
        "servings_assumed": assumed,
        "ingredients": merged_ingredients,
        "steps": steps,
        "source": "generator+extractor",
        "model": model_id,
    }

    _cache_store(
        key_hash=key_hash,
        query=query,
        servings=gen_servings_int,
        provider=GEN_PROVIDER,
        model=model_id,
        response_json=payload,
    )

    return payload
