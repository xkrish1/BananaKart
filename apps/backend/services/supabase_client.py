"""Compatibility imports for legacy routes."""

from ..supabase_client import insert_eco_result, insert_recipe, supabase

__all__ = ["supabase", "insert_recipe", "insert_eco_result"]
